#!/usr/bin/env python3
"""Check which modules are deployed on prod (sepal.io) and test (test.sepal.io)."""

import base64
import json
import os
import urllib.request
from pathlib import Path

from models import DeployStatus, SepalAppList, get_deploy_status

SECRETS_FILE = Path.home() / "1_modules/scripts/sepal-contrib/set_environment/my.secrets.env"


def load_secrets() -> dict[str, str]:
    """Load key=value pairs from the secrets env file."""
    secrets = {}
    if SECRETS_FILE.exists():
        for line in SECRETS_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                secrets[key.strip()] = value.strip()
    return secrets


def get_credential(key: str, secrets: dict[str, str]) -> str | None:
    """Look up a credential from env, falling back to the secrets file."""
    return os.environ.get(key) or secrets.get(key)


def fetch_apps(host: str, user: str, password: str) -> SepalAppList:
    """Fetch and parse the app list from a SEPAL server."""
    url = f"https://{host}/api/apps/list"
    credentials = base64.b64encode(f"{user}:{password}".encode()).decode()
    req = urllib.request.Request(url, headers={"Authorization": f"Basic {credentials}"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    return SepalAppList.model_validate(data)


def main():
    secrets = load_secrets()

    user = get_credential("SEPAL_USER", secrets)
    password = get_credential("SEPAL_PASSWORD", secrets)
    user_test = get_credential("SEPAL_USER_TESTENV", secrets)
    password_test = get_credential("SEPAL_PASSWORD_TESTENV", secrets)

    if not user or not password:
        raise SystemExit("SEPAL_USER and SEPAL_PASSWORD must be set (env or secrets file)")
    if not user_test or not password_test:
        raise SystemExit("SEPAL_USER_TESTENV and SEPAL_PASSWORD_TESTENV must be set (env or secrets file)")

    print("Fetching app list from sepal.io …")
    prod_apps = fetch_apps("sepal.io", user, password)
    prod_by_repo = prod_apps.by_repo()

    print("Fetching app list from test.sepal.io …")
    test_apps = fetch_apps("test.sepal.io", user_test, password_test)
    test_by_repo = test_apps.by_repo()

    project_root = Path(__file__).parent.parent
    modules_path = project_root / "modules.json"
    with open(modules_path) as f:
        data = json.load(f)

    updated = 0
    for cat in data["categories"]:
        for mod in cat["modules"]:
            github_url = mod.get("github_url", "")
            prod_status = get_deploy_status(prod_by_repo.get(github_url)).value
            test_status = get_deploy_status(test_by_repo.get(github_url)).value

            if mod.get("on_prod") != prod_status or mod.get("on_test") != test_status:
                updated += 1
            mod["on_prod"] = prod_status
            mod["on_test"] = test_status

    with open(modules_path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

    print(f"Updated {updated} module(s) in modules.json")


if __name__ == "__main__":
    main()
