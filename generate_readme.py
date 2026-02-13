#!/usr/bin/env python3
"""Generate README.rst from modules.json and README.rst.j2."""

import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


def badge_ref(name: str) -> str:
    """Convert module name to badge reference name."""
    return name.replace("-", "_").replace(".", "_") + "_badge"


def get_workflow(mod: dict) -> str:
    """Get the workflow filename for a module."""
    return mod.get("badge_workflow", "unit.yaml")


def pad(value, width: int) -> str:
    """Left-align a string within a field of given width."""
    return str(value).ljust(width)


def main():
    base = Path(__file__).parent
    with open(base / "modules.json") as f:
        data = json.load(f)

    # Flatten all modules across categories for the link/badge sections
    all_modules = []
    for cat in data["categories"]:
        for mod in cat["modules"]:
            all_modules.append(mod)

    env = Environment(
        loader=FileSystemLoader(base),
        keep_trailing_newline=True,
    )
    env.filters["badge_ref"] = badge_ref
    env.filters["pad"] = pad
    env.globals["badge_ref"] = badge_ref
    env.globals["get_workflow"] = get_workflow

    template = env.get_template("README.rst.j2")
    output = template.render(categories=data["categories"], all_modules=all_modules)
    (base / "README.rst").write_text(output)
    print("README.rst generated successfully.")


if __name__ == "__main__":
    main()
