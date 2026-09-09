#!/usr/bin/env python3
"""Sync modules.json deployment status from the sepal-apps-catalog.

The catalog is what SEPAL actually reads: app-manager and app-launcher fetch
apps.{test,prod}.json at runtime and serve what they find there, so it is the
source of truth for what is deployed where.

This used to ask https://<host>/api/apps/list instead. That endpoint is served
by app-manager from the same catalog, so it carried no extra information -- and
it is strictly less reliable, because app-manager falls back to a cached
apps.json on disk when the fetch fails, which makes the API lag the catalog
silently. Reading the catalog directly also drops the credential requirement.

Besides updating on_prod/on_test, this reports drift it cannot fix on its own:
apps the catalog serves that modules.json has never heard of, and tags that apps
use but the catalog never declares (the GUI builds its tag filter from the
catalog's root `tags` list, so an undeclared tag has no label to filter by).
"""

import json
import urllib.request
from pathlib import Path

from models import SepalAppList, get_deploy_status

CATALOG_REPO = "dfguerrerom/sepal-apps-catalog"
CATALOG_BRANCH = "main"
CATALOGS = {"prod": "apps.prod.json", "test": "apps.test.json"}


def normalize(url: str) -> str:
    """Compare repository URLs without tripping over trailing slashes or .git."""
    return (url or "").strip().rstrip("/").removesuffix(".git").lower()


def fetch_catalog(filename: str) -> dict:
    url = f"https://raw.githubusercontent.com/{CATALOG_REPO}/{CATALOG_BRANCH}/{filename}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.loads(resp.read())


def undeclared_tags(raw: dict) -> set[str]:
    """Tags used by an app but absent from the catalog's own root vocabulary."""
    declared = {t.get("value") for t in raw.get("tags", []) if isinstance(t, dict)}
    used = set()

    def walk(apps):
        for app in apps:
            used.update(app.get("tags") or [])
            walk(app.get("apps") or [])

    walk(raw.get("apps", []))
    return used - declared


def main():
    project_root = Path(__file__).parent.parent
    modules_path = project_root / "modules.json"
    data = json.loads(modules_path.read_text())

    by_server = {}
    for server, filename in CATALOGS.items():
        print(f"Fetching {filename} from {CATALOG_REPO}@{CATALOG_BRANCH} …")
        raw = fetch_catalog(filename)
        apps = SepalAppList.model_validate(raw)
        by_server[server] = {normalize(repo): app for repo, app in apps.by_repo().items()}

        missing = undeclared_tags(raw)
        if missing:
            print(f"  {filename}: tags used but not declared in the root `tags` list: "
                  f"{', '.join(sorted(missing))}")

    tracked = set()
    updated = 0
    for cat in data["categories"]:
        for mod in cat["modules"]:
            repo = normalize(mod.get("github_url", ""))
            tracked.add(repo)
            for server in CATALOGS:
                status = get_deploy_status(by_server[server].get(repo)).value
                key = f"on_{server}"
                if mod.get(key) != status:
                    print(f"  {mod['name']}: {key} {mod.get(key)} -> {status}")
                    updated += 1
                mod[key] = status

    modules_path.write_text(json.dumps(data, indent=2) + "\n")
    print(f"\nUpdated {updated} field(s) in modules.json")

    # Apps the catalog serves that nothing in modules.json points at. Placing them
    # in the right category is a judgement call, so they are reported, not added.
    untracked = {}
    for server, apps in by_server.items():
        for repo, app in apps.items():
            if repo not in tracked:
                untracked.setdefault(repo, (app.label, []))[1].append(server)
    if untracked:
        print(f"\nIn the catalog but not tracked in modules.json ({len(untracked)}):")
        for repo, (label, servers) in sorted(untracked.items()):
            owner_repo = "/".join(repo.split("/")[-2:])
            print(f"  {owner_repo:<34} {label}  [{', '.join(sorted(servers))}]")

    # The same app pointing at different repositories per server is a catalog bug:
    # the two environments would build from different sources.
    by_name = {}
    for server, apps in by_server.items():
        for repo in apps:
            by_name.setdefault(repo.split("/")[-1], {})[server] = repo
    forked = {n: s for n, s in by_name.items() if len(set(s.values())) > 1}
    if forked:
        print(f"\nSame app, different repository per server ({len(forked)}):")
        for name, servers in sorted(forked.items()):
            for server, repo in sorted(servers.items()):
                print(f"  {name:<20} {server:<5} {repo}")


if __name__ == "__main__":
    main()
