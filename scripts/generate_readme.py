#!/usr/bin/env python3
"""Generate README.rst from modules.json and README.rst.j2."""

import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


def badge_ref(name: str, workflow: str = "") -> str:
    """Convert module name to badge reference name."""
    base = name.replace("-", "_").replace(".", "_")
    if workflow:
        suffix = workflow.replace(".yaml", "").replace(".yml", "")
        return f"{base}_{suffix}_badge"
    return f"{base}_badge"


def get_workflows(mod: dict) -> list[str]:
    """Get the workflow filenames for a module."""
    if mod.get("badge_workflows"):
        return mod["badge_workflows"]
    if mod.get("badge_workflow"):
        return [mod["badge_workflow"]]
    if mod.get("ci") and not mod["ci"].get("skip"):
        return ["ci.yaml"]
    return []


def pad(value, width: int) -> str:
    """Left-align a string within a field of given width."""
    return str(value).ljust(width)


_SERVER_ICONS = {"active": "\u2713", "hidden": "\u25cb"}


def badge_cells(mod: dict) -> str:
    """Return RST badge references for all workflows of a module."""
    workflows = get_workflows(mod)
    parts = [f"|{badge_ref(mod['name'], wf)}|_" for wf in workflows]
    return "  ".join(parts)


def server_icon(mod: dict, key: str) -> str:
    """Return an icon for the module's deployment status on a server.

    ✓ = active, ○ = hidden, (blank) = missing.
    """
    return _SERVER_ICONS.get(mod.get(key, ""), "")


def migration_label(mod: dict) -> str:
    """Short migration-state label for the README table.

    Combines `migration.status` with `migration.merge_target` (short form)
    and optional `migration.migrated_route` into a single cell, e.g.:

        done → sepal-gee-bundle /gfc
        audited
        skip
    """
    mig = mod.get("migration") or {}
    status = mig.get("status") or ""
    target = mig.get("merge_target") or ""
    route = mig.get("migrated_route") or ""
    if status == "done" and target:
        short_target = target.split("/")[-1] if "/" in target else target
        if route:
            return f"done → {route}"
        return f"done → {short_target}"
    return status


def main():
    scripts_dir = Path(__file__).parent
    project_root = scripts_dir.parent
    with open(project_root / "modules.json") as f:
        data = json.load(f)

    # Flatten all modules across categories for the link/badge sections
    all_modules = []
    for cat in data["categories"]:
        for mod in cat["modules"]:
            all_modules.append(mod)

    env = Environment(
        loader=FileSystemLoader(scripts_dir),
        keep_trailing_newline=True,
    )
    env.filters["badge_ref"] = badge_ref
    env.filters["pad"] = pad
    env.globals["badge_ref"] = badge_ref
    env.globals["get_workflows"] = get_workflows
    env.globals["badge_cells"] = badge_cells
    env.globals["server_icon"] = server_icon
    env.globals["migration_label"] = migration_label

    template = env.get_template("README.rst.j2")
    output = template.render(categories=data["categories"], all_modules=all_modules)
    (project_root / "README.rst").write_text(output)
    print("README.rst generated successfully.")


if __name__ == "__main__":
    main()
