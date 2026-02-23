#!/usr/bin/env python3
"""Generate per-repo CLAUDE.md files from audit_data.json.

Reads the gathered audit data and writes a CLAUDE.md migration playbook
into each module's repo directory. Also ensures CLAUDE.md is in .gitignore.
"""

import json
import re
from pathlib import Path
from datetime import date

BASE = Path("/home/dguerrero/1_modules")
TODAY = date.today().isoformat()

# Module name mapping (local_dir -> display name from modules.json)
NAME_MAP = {
    "sepal_pysmm": "sepal_pysmm",
    "gfc_wrapper_python": "gfc_wrapper_python",
    "vector_manager": "vector_manager",
    "clip-time-series": "clip-time-series",
    "alos_mosaics": "alos_mosaics",
    "sdg_15.3.1": "sdg_15.3.1",
    "tmf_sepal": "tmf_sepal",
    "planet-order": "planet-order",
    "coverage_analysis": "coverage_analysis",
    "fcdm": "fcdm",
    "basin-rivers": "basin-rivers",
    "gee_source": "gee_source",
    "active-fires-explorer": "active_fires_explorer",
    "sepal_smfm_biota": "sepal_smfm_biota",
    "gwb": "gwb",
    "cumsum_change": "cumsum_change",
    "weplan": "weplan",
    "sepal-leafmap": "sepal-leafmap",
    "eSBAE_notebooks": "eSBAE_notebooks",
    "deforestation-alerts-module": "deforestation-alerts",
}

GITHUB_MAP = {
    "sepal_pysmm": "https://github.com/sepal-contrib/sepal_pysmm",
    "gfc_wrapper_python": "https://github.com/sepal-contrib/gfc_wrapper_python",
    "vector_manager": "https://github.com/sepal-contrib/vector_manager",
    "clip-time-series": "https://github.com/sepal-contrib/clip-time-series",
    "alos_mosaics": "https://github.com/sepal-contrib/alos_mosaics",
    "sdg_15.3.1": "https://github.com/sepal-contrib/sdg_15.3.1",
    "tmf_sepal": "https://github.com/sepal-contrib/tmf_sepal",
    "planet-order": "https://github.com/sepal-contrib/planet-order",
    "coverage_analysis": "https://github.com/sepal-contrib/coverage_analysis",
    "fcdm": "https://github.com/sepal-contrib/fcdm",
    "basin-rivers": "https://github.com/sepal-contrib/basin-rivers",
    "gee_source": "https://github.com/sepal-contrib/gee_source",
    "active-fires-explorer": "https://github.com/sepal-contrib/planet_active_fires_explorer",
    "sepal_smfm_biota": "https://github.com/sepal-contrib/sepal_smfm_biota",
    "gwb": "https://github.com/sepal-contrib/gwb",
    "cumsum_change": "https://github.com/sepal-contrib/cumsum_change",
    "weplan": "https://github.com/sepal-contrib/weplan",
    "sepal-leafmap": "https://github.com/sepal-contrib/sepal-leafmap",
    "eSBAE_notebooks": "https://github.com/sepal-contrib/eSBAE_notebooks",
    "deforestation-alerts-module": "https://github.com/sepal-contrib/deforestation-alerts-module",
}

# Purpose descriptions derived from README/code analysis
PURPOSE_MAP = {
    "sepal_pysmm": "Soil Moisture Mapping tool using Sentinel-1 SAR data via Google Earth Engine. Estimates surface soil moisture at plot and landscape scales.",
    "gfc_wrapper_python": "Wrapper around Hansen Global Forest Change (GFC) dataset for analyzing deforestation and forest cover change via GEE.",
    "vector_manager": "Manages vector/AOI (Area of Interest) assets — upload, select, and manage GEE vector assets for use in other SEPAL modules.",
    "clip-time-series": "Clips satellite time-series imagery to user-defined AOIs and generates downloadable mosaics and animations.",
    "alos_mosaics": "Access and process ALOS PALSAR/PALSAR-2 yearly mosaic data for forest/non-forest classification via GEE.",
    "sdg_15.3.1": "Computes SDG Indicator 15.3.1 (Land Degradation Neutrality) using sub-indicators for land cover, productivity, and soil organic carbon via GEE.",
    "tmf_sepal": "Tropical Moist Forests (TMF) analysis tool — visualizes JRC TMF dataset for deforestation and degradation monitoring via GEE.",
    "planet-order": "Orders and downloads Planet satellite imagery (PlanetScope, SkySat) through the Planet Orders API.",
    "coverage_analysis": "Analyzes spatial coverage of satellite imagery collections (Landsat, Sentinel) over user-defined AOIs via GEE.",
    "fcdm": "Forest Cover Disturbance Monitoring — detects forest canopy disturbances using Sentinel-2 and Landsat time series via GEE.",
    "basin-rivers": "Hydrological basin and river network analysis using HydroSHEDS data. Delineates watersheds and river networks via GEE.",
    "gee_source": "Browser/explorer for Google Earth Engine data catalog. Lets users search, preview, and add GEE datasets to the map.",
    "active-fires-explorer": "Explores active fire alerts using Planet/FIRMS data. Visualizes fire hotspots and provides analysis tools.",
    "sepal_smfm_biota": "SMFM (Satellite Monitoring for Forest Management) BIOTA tool — estimates above-ground biomass from ALOS PALSAR data.",
    "gwb": "GuidosToolbox Workbench — provides 10+ morphological spatial pattern analysis tools (MSPA, fragmentation, connectivity, etc.) for binary map inputs.",
    "cumsum_change": "Cumulative sum (CUSUM) change detection algorithm for identifying abrupt changes in satellite time series.",
    "weplan": "Conservation planning tool using Marxan algorithm. Optimizes spatial priorities for land-use planning.",
    "sepal-leafmap": "Leafmap integration for SEPAL — provides an interactive map viewer with leafmap's geospatial visualization capabilities.",
    "eSBAE_notebooks": "Enhanced Sampling-Based Area Estimation notebooks — Jupyter notebooks for statistical sampling design and area estimation workflows.",
    "deforestation-alerts-module": "Aggregates and visualizes near-real-time deforestation alerts (GLAD, RADD, CCDC) with GEE integration for AOI-based monitoring.",
}


def assess_complexity(data):
    """Determine migration complexity from gathered data."""
    counts = data.get("component_counts", {})
    tiles = counts.get("tiles", 0)
    models = counts.get("models", 0)
    widgets = counts.get("widgets", 0)
    total = tiles + models + widgets

    uses_gee = data.get("uses_gee", False)
    uses_planet = data.get("uses_planet", False)

    if total <= 4 and not uses_planet:
        return "low", "few components, standard sepal_ui patterns"
    elif total <= 10:
        reasons = []
        if uses_gee:
            reasons.append("GEE integration")
        if uses_planet:
            reasons.append("Planet API")
        if widgets > 3:
            reasons.append(f"{widgets} custom widgets")
        if tiles > 4:
            reasons.append(f"{tiles} tiles")
        return "medium", ", ".join(reasons) if reasons else "moderate component count"
    else:
        reasons = [f"{total} total components"]
        if widgets > 5:
            reasons.append(f"{widgets} custom widgets")
        if models > 3:
            reasons.append(f"{models} models")
        return "high", ", ".join(reasons)


def extract_drawer_items(ui_source):
    """Extract DrawerItem names from ui.ipynb source."""
    if not ui_source:
        return []
    items = []
    # Match DrawerItem(..., title="Name", ...) or DrawerItem("Name", ...)
    for match in re.finditer(r'DrawerItem\s*\([^)]*?["\']([^"\']+)["\']', ui_source):
        items.append(match.group(1))
    # Also match title= pattern
    for match in re.finditer(r'title\s*=\s*["\']([^"\']+)["\']', ui_source):
        title = match.group(1)
        if title not in items and len(title) < 40:
            items.append(title)
    return items


def extract_python_version(data):
    """Extract Python version from sepal_environment.yml."""
    env = data.get("sepal_environment_yml", "")
    if not env:
        return "3.10"
    for line in env.split("\n"):
        if "python" in line.lower() and ("3." in line):
            match = re.search(r"3\.\d+", line)
            if match:
                return match.group()
    return "3.10"


def extract_sepal_ui_ver(data):
    """Clean sepal_ui version string."""
    raw = data.get("sepal_ui_version", "")
    if not raw:
        return "unknown"
    # Clean up to just version
    match = re.search(r"sepal[_-]ui[=><!]*=*([\d.]+)", raw)
    if match:
        return match.group(1)
    return raw.strip()


def get_component_subdirs(data):
    """Parse component tree to get subdirectory names."""
    tree = data.get("component_tree", "")
    if not tree or tree == "[no component/ directory]":
        return []
    dirs = []
    for line in tree.split("\n"):
        # Look for top-level dirs (├── or └──)
        match = re.match(r'^[├└]── (\w+)$', line)
        if match:
            dirs.append(match.group(1))
    return dirs


def generate_claude_md(local_dir, data):
    """Generate CLAUDE.md content for a repo."""
    name = NAME_MAP.get(local_dir, local_dir)
    github = GITHUB_MAP.get(local_dir, "")
    purpose = PURPOSE_MAP.get(local_dir, "SEPAL geospatial analysis module.")
    counts = data.get("component_counts", {})
    tiles = counts.get("tiles", 0)
    models = counts.get("models", 0)
    widgets = counts.get("widgets", 0)
    scripts = counts.get("scripts", 0)

    complexity, complexity_reason = assess_complexity(data)

    apis = []
    if data.get("uses_gee"):
        apis.append("GEE")
    if data.get("uses_planet"):
        apis.append("Planet API")
    api_str = ", ".join(apis) if apis else "None"

    python_ver = extract_python_version(data)
    sui_ver = extract_sepal_ui_ver(data)
    comp_dirs = get_component_subdirs(data)
    comp_str = ", ".join(comp_dirs) if comp_dirs else "unknown"

    has_tests = "Yes" if data.get("has_tests") else "No"
    ci_workflows = data.get("ci_workflows", [])
    ci_str = ", ".join(ci_workflows) if ci_workflows else "None"

    drawer_items = extract_drawer_items(data.get("ui_ipynb", ""))

    # Determine entry point
    if data.get("ui_ipynb"):
        entry = "ui.ipynb"
    elif data.get("entry_app_py"):
        entry = "app.py (already exists!)"
    else:
        entry = "unknown (no ui.ipynb found)"

    # Special case for eSBAE_notebooks
    is_notebooks = local_dir == "eSBAE_notebooks"

    # Build assessment
    assessment_parts = []
    if sui_ver and sui_ver != "unknown":
        if sui_ver.startswith("2.2"):
            assessment_parts.append(f"Uses sepal_ui {sui_ver} which is relatively recent.")
        elif sui_ver.startswith("2.1") or sui_ver.startswith("2.0"):
            assessment_parts.append(f"Uses sepal_ui {sui_ver} — may need API updates for sepal_ui >= 3.x.")
        else:
            assessment_parts.append(f"Uses sepal_ui {sui_ver}.")

    if data.get("uses_gee"):
        assessment_parts.append("Heavy GEE integration — all GEE calls should work unchanged, but session initialization must be handled in Solara context.")

    if data.get("uses_planet"):
        assessment_parts.append("Uses Planet API — need to verify API key handling works in Solara multi-user context.")

    if widgets > 5:
        assessment_parts.append(f"Has {widgets} custom widgets — these may need adaptation for Solara rendering.")
    elif widgets > 0:
        assessment_parts.append(f"Has {widgets} custom widget(s) — should migrate straightforwardly if based on sepal_ui base classes.")

    if is_notebooks:
        assessment_parts.append("This is a notebooks-based module, NOT a standard sepal_ui app. Migration approach will be fundamentally different — may need to be rebuilt from scratch or evaluated for consolidation with sbae-design.")

    if not data.get("has_tests"):
        assessment_parts.append("No test suite — testing will rely on manual verification with `solara run app.py`.")

    if tiles > 10:
        assessment_parts.append(f"Large module with {tiles} tiles — will need careful mapping of all DrawerItems to steps_data entries.")

    assessment = "\n\n".join(assessment_parts) if assessment_parts else "Standard sepal_ui module. Migration should follow the reference pattern closely."

    # Build migration steps
    migration_steps = [
        "Create app.py with MapApp layout + Page component",
        "Convert tile instantiation from ui.ipynb notebook cells to Page() body",
    ]

    if drawer_items:
        items_str = ", ".join(f'"{d}"' for d in drawer_items[:8])
        migration_steps.append(f"Map DrawerItems ({items_str}) to steps_data entries")
    else:
        migration_steps.append("Map DrawerItems to steps_data entries")

    migration_steps.extend([
        "Add session management (setup_sessions, on_kernel_start)",
        "Add theme support (ThemeToggle, setup_theme_colors)",
    ])

    if data.get("uses_gee"):
        migration_steps.append("Verify GEE initialization works in Solara context (ee.Initialize in on_kernel_start)")

    if data.get("uses_planet"):
        migration_steps.append("Verify Planet API key handling in multi-user Solara context")

    migration_steps.extend([
        "Update sepal_environment.yml (Python 3.12, sepal_ui>=3.1.1)",
        "Test with `solara run app.py --port 8901`",
    ])

    if widgets > 3:
        migration_steps.append(f"Audit and adapt {widgets} custom widgets for Solara compatibility")

    migration_steps_str = "\n".join(f"- [ ] {s}" for s in migration_steps)

    # Merge candidate analysis
    merge_analysis = "No obvious merge candidate — this module has a unique function."
    if local_dir == "eSBAE_notebooks":
        merge_analysis = "Strong merge candidate with **sbae-design**. Both relate to sampling-based area estimation. eSBAE_notebooks provides the statistical/notebook workflows while sbae-design is the Solara app. Consider consolidating notebook functionality into sbae-design."
    elif local_dir == "gee_source":
        merge_analysis = "Utility module — may become less relevant if other modules integrate their own data browsing. Could be kept as a standalone lightweight tool."
    elif local_dir == "sepal-leafmap":
        merge_analysis = "Thin wrapper around leafmap. Evaluate whether this should remain a standalone module or be integrated as a map option in sepal_ui."
    elif local_dir == "sepal_smfm_biota":
        merge_analysis = "Related to smfm_deforest (external, skipped). Standalone module for biomass estimation."
    elif local_dir == "cumsum_change":
        merge_analysis = "Change detection module — functionally distinct but could potentially be combined with other change detection tools (fcdm) in the future."

    # Known issues
    issues = []
    if not ci_workflows:
        issues.append("No CI workflows configured")
    if not data.get("has_tests"):
        issues.append("No automated tests")
    if python_ver == "3.10":
        issues.append("Targets Python 3.10 — needs upgrade to 3.12 for Solara compatibility")
    if is_notebooks:
        issues.append("Not a standard sepal_ui module — notebook-based architecture")

    issues_str = "\n".join(f"- {i}" for i in issues) if issues else "None identified during automated scan. Manual review recommended."

    # Assemble full CLAUDE.md
    md = f"""# CLAUDE.md — {name}

## Module Overview
- **Purpose**: {purpose}
- **Repo**: {github}
- **Status**: not_started
- **Complexity**: {complexity} — {complexity_reason}

## Current Architecture
- Entry point: {entry}
- Component structure: component/{{{comp_str}}}
- {tiles} tiles, {models} models, {widgets} widgets, {scripts} scripts
- External APIs: {api_str}
- sepal_ui version: {sui_ver}
- Python version: {python_ver}
- Tests: {has_tests}
- CI: {ci_str}

## Assessment
{assessment}

## Migration Plan
### Target: Pure Solara app following sbae-design pattern
{migration_steps_str}

## Merge Candidate Analysis
{merge_analysis}

## Known Issues
{issues_str}

## Session Log
| Date | Summary |
|------|---------|
| {TODAY} | Initial audit — CLAUDE.md created |
"""
    return md, complexity


def ensure_gitignore(repo_path):
    """Ensure CLAUDE.md is in .gitignore."""
    gi_path = repo_path / ".gitignore"
    if gi_path.exists():
        content = gi_path.read_text()
        if "CLAUDE.md" not in content:
            with open(gi_path, "a") as f:
                if not content.endswith("\n"):
                    f.write("\n")
                f.write("CLAUDE.md\n")
            return "appended"
        return "already present"
    else:
        gi_path.write_text("CLAUDE.md\n")
        return "created"


def main():
    data_path = BASE / "module_monitor" / "audit_data.json"
    with open(data_path) as f:
        all_data = json.load(f)

    results = {}
    for local_dir, data in all_data.items():
        if "error" in data:
            print(f"SKIP  {local_dir}: {data['error']}")
            continue

        md_content, complexity = generate_claude_md(local_dir, data)
        repo_path = BASE / local_dir

        # Write CLAUDE.md
        claude_path = repo_path / "CLAUDE.md"
        claude_path.write_text(md_content)

        # Ensure .gitignore
        gi_status = ensure_gitignore(repo_path)

        results[local_dir] = {"complexity": complexity, "gitignore": gi_status}
        print(f"WROTE {local_dir}/CLAUDE.md ({complexity} complexity, .gitignore: {gi_status})")

    print(f"\nTotal: {len(results)} CLAUDE.md files written")

    # Summary
    complexities = [r["complexity"] for r in results.values()]
    print(f"  Low: {complexities.count('low')}")
    print(f"  Medium: {complexities.count('medium')}")
    print(f"  High: {complexities.count('high')}")


if __name__ == "__main__":
    main()
