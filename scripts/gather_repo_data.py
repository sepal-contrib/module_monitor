#!/usr/bin/env python3
"""Gather structured data from all module repos for audit."""

import json
import os
from pathlib import Path

BASE = Path("/home/dguerrero/1_modules")

REPOS = [
    "sepal_pysmm", "gfc_wrapper_python", "vector_manager", "clip-time-series",
    "alos_mosaics", "sdg_15.3.1", "tmf_sepal", "planet-order",
    "coverage_analysis", "fcdm", "basin-rivers", "gee_source",
    "active-fires-explorer", "sepal_smfm_biota", "gwb", "cumsum_change",
    "weplan", "sepal-leafmap", "eSBAE_notebooks", "deforestation-alerts-module",
]


def safe_read(path, max_lines=200):
    """Read file, return content or None."""
    try:
        with open(path) as f:
            lines = f.readlines()
        if len(lines) > max_lines:
            return "".join(lines[:max_lines]) + f"\n... ({len(lines)} total lines)"
        return "".join(lines)
    except Exception:
        return None


def get_tree(root, max_depth=3, prefix=""):
    """Get directory tree as string."""
    entries = []
    try:
        items = sorted(os.listdir(root))
    except PermissionError:
        return ["[permission denied]"]

    # Skip common non-essential dirs
    skip = {".git", "__pycache__", ".ipynb_checkpoints", "node_modules", ".mypy_cache", ".ruff_cache"}
    items = [i for i in items if i not in skip]

    for i, item in enumerate(items):
        path = os.path.join(root, item)
        is_last = i == len(items) - 1
        connector = "└── " if is_last else "├── "
        entries.append(f"{prefix}{connector}{item}")
        if os.path.isdir(path) and max_depth > 1:
            extension = "    " if is_last else "│   "
            entries.extend(get_tree(path, max_depth - 1, prefix + extension))
    return entries


def count_component_files(comp_dir):
    """Count tiles, models, widgets, scripts in component/."""
    counts = {"tiles": 0, "models": 0, "widgets": 0, "scripts": 0, "other": 0}
    if not comp_dir.is_dir():
        return counts
    for sub in comp_dir.iterdir():
        if sub.is_dir():
            name = sub.name.lower()
            py_files = list(sub.glob("*.py"))
            n = len([f for f in py_files if f.name != "__init__.py"])
            if "tile" in name:
                counts["tiles"] = n
            elif "model" in name:
                counts["models"] = n
            elif "widget" in name:
                counts["widgets"] = n
            elif "script" in name:
                counts["scripts"] = n
            else:
                counts["other"] += n
        elif sub.suffix == ".py" and sub.name != "__init__.py":
            counts["other"] += 1
    return counts


def check_gee_usage(repo_path):
    """Check if repo uses GEE."""
    for py_file in repo_path.rglob("*.py"):
        try:
            content = py_file.read_text(errors="ignore")
            if "import ee" in content or "ee.Initialize" in content:
                return True
        except Exception:
            pass
    return False


def check_planet_usage(repo_path):
    """Check if repo uses Planet API."""
    for py_file in repo_path.rglob("*.py"):
        try:
            content = py_file.read_text(errors="ignore")
            if "planet" in content.lower() and ("api" in content.lower() or "Planet" in content):
                return True
        except Exception:
            pass
    return False


def get_sepal_ui_version(repo_path):
    """Extract sepal_ui version from requirements."""
    for fname in ["requirements.txt", "sepal_environment.yml"]:
        fpath = repo_path / fname
        if fpath.exists():
            content = fpath.read_text(errors="ignore")
            for line in content.split("\n"):
                if "sepal_ui" in line or "sepal-ui" in line:
                    return line.strip()
    return None


def analyze_repo(local_dir):
    """Analyze a single repo."""
    repo = BASE / local_dir
    if not repo.is_dir():
        return {"error": f"Directory not found: {repo}"}

    data = {"local_dir": local_dir, "path": str(repo)}

    # Tree structure (depth 3)
    data["tree"] = "\n".join(get_tree(str(repo), max_depth=3))

    # ui.ipynb
    ui_path = repo / "ui.ipynb"
    if ui_path.exists():
        raw = safe_read(ui_path, max_lines=300)
        if raw:
            # Extract just the source cells (not outputs)
            try:
                nb = json.loads(raw if "total lines" not in raw else open(ui_path).read())
                sources = []
                for cell in nb.get("cells", []):
                    if cell.get("cell_type") == "code":
                        src = "".join(cell.get("source", []))
                        if src.strip():
                            sources.append(src)
                data["ui_ipynb"] = "\n---\n".join(sources)
            except Exception:
                data["ui_ipynb"] = "[parse error]"
    else:
        # Check for alternative entry points
        for alt in ["app.py", "solara_app.py", "main.py"]:
            alt_path = repo / alt
            if alt_path.exists():
                data[f"entry_{alt}"] = safe_read(alt_path, max_lines=100)

    # Component structure
    comp_dir = repo / "component"
    if comp_dir.is_dir():
        data["component_tree"] = "\n".join(get_tree(str(comp_dir), max_depth=3))
        data["component_counts"] = count_component_files(comp_dir)
    else:
        data["component_tree"] = "[no component/ directory]"
        data["component_counts"] = {}

    # Dependencies
    for fname in ["requirements.txt", "sepal_environment.yml", "pyproject.toml"]:
        fpath = repo / fname
        if fpath.exists():
            data[fname.replace(".", "_")] = safe_read(fpath, max_lines=80)

    # GEE and Planet
    data["uses_gee"] = check_gee_usage(repo)
    data["uses_planet"] = check_planet_usage(repo)
    data["sepal_ui_version"] = get_sepal_ui_version(repo)

    # .gitignore
    gi = repo / ".gitignore"
    data["has_gitignore"] = gi.exists()
    if gi.exists():
        content = gi.read_text(errors="ignore")
        data["claude_in_gitignore"] = "CLAUDE.md" in content
    else:
        data["claude_in_gitignore"] = False

    # Check for existing solara/app.py
    data["has_app_py"] = (repo / "app.py").exists()
    data["has_solara_app"] = (repo / "solara_app.py").exists()

    # Check for tests
    data["has_tests"] = (repo / "tests").is_dir() or (repo / "test").is_dir()

    # Check for CI
    gh_dir = repo / ".github" / "workflows"
    if gh_dir.is_dir():
        data["ci_workflows"] = [f.name for f in gh_dir.iterdir() if f.suffix in (".yml", ".yaml")]
    else:
        data["ci_workflows"] = []

    # README
    for rname in ["README.md", "README.rst"]:
        rpath = repo / rname
        if rpath.exists():
            data["readme_excerpt"] = safe_read(rpath, max_lines=30)
            break

    return data


def main():
    results = {}
    for local_dir in REPOS:
        print(f"Analyzing {local_dir}...")
        results[local_dir] = analyze_repo(local_dir)

    output_path = BASE / "module_monitor" / "audit_data.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nData written to {output_path}")
    print(f"Repos analyzed: {len(results)}")


if __name__ == "__main__":
    main()
