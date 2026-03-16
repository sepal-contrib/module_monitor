#!/usr/bin/env python3
"""Sync CI workflow files to module repos.

Reads modules.json and renders ci.yaml.j2 for each eligible
Jupyter/Conda module, writing the result to
<repo>/.github/workflows/ci.yaml.
"""

import json
from pathlib import Path

import jinja2

BASE = Path("/home/dguerrero/1_modules")
SCRIPTS = Path(__file__).parent
MODULES_JSON = SCRIPTS.parent / "modules.json"

SKIP_STATUSES = {"done", "skip"}


def load_modules():
    """Return the Jupyter/Conda Modules list from modules.json."""
    with open(MODULES_JSON) as f:
        data = json.load(f)
    for cat in data["categories"]:
        if cat["name"] == "Jupyter/Conda Modules":
            return cat["modules"]
    return []


def main():
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(SCRIPTS)),
        keep_trailing_newline=True,
    )
    template = env.get_template("ci.yaml.j2")

    modules = load_modules()
    written = []
    skipped = []

    for mod in modules:
        name = mod["name"]
        local_dir = mod.get("local_dir")
        migration = mod.get("migration", {})
        ci = mod.get("ci", {})

        # Skip criteria
        if not local_dir:
            skipped.append((name, "no local_dir"))
            continue
        if ci.get("skip"):
            skipped.append((name, "ci.skip=true"))
            continue
        if migration.get("status") in SKIP_STATUSES:
            skipped.append((name, f"status={migration['status']}"))
            continue

        # Render template
        rendered = template.render(
            notebook=ci.get("notebook", "ui.ipynb"),
            secrets=ci.get("secrets", []),
        )

        # Write to repo
        dest = BASE / local_dir / ".github" / "workflows" / "ci.yaml"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(rendered)

        written.append(name)
        print(f"WROTE {local_dir}/.github/workflows/ci.yaml")

    # Summary
    for name, reason in skipped:
        print(f"SKIP  {name}: {reason}")

    print(f"\nTotal: {len(written)} written, {len(skipped)} skipped")


if __name__ == "__main__":
    main()
