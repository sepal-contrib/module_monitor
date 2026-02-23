#!/usr/bin/env python3
"""Generate CLAUDE.md from modules.json and CLAUDE_MASTER.md.j2."""

import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


def main():
    scripts_dir = Path(__file__).parent
    project_root = scripts_dir.parent

    with open(project_root / "modules.json") as f:
        data = json.load(f)

    # Extract Jupyter/Conda modules (those with migration field)
    jupyter_modules = []
    for cat in data["categories"]:
        for mod in cat["modules"]:
            if "migration" in mod:
                jupyter_modules.append(mod)

    # Count statuses
    statuses = [m["migration"]["status"] for m in jupyter_modules]
    counts = {
        "done": statuses.count("done"),
        "in_progress": statuses.count("in_progress"),
        "audited": statuses.count("audited"),
        "blocked": statuses.count("blocked"),
        "skip": statuses.count("skip"),
        "not_started": statuses.count("not_started"),
    }

    # Find merge candidates
    merge_candidates = [
        m for m in jupyter_modules if m["migration"].get("merge_candidate")
    ]

    env = Environment(
        loader=FileSystemLoader(scripts_dir),
        keep_trailing_newline=True,
    )

    template = env.get_template("CLAUDE_MASTER.md.j2")
    output = template.render(
        jupyter_modules=jupyter_modules,
        counts=counts,
        merge_candidates=merge_candidates,
    )

    (project_root / "CLAUDE.md").write_text(output)
    print("CLAUDE.md generated successfully.")


if __name__ == "__main__":
    main()
