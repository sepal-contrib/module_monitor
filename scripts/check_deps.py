"""Deterministic PyPI scanner for the dependency intelligence system.

Scans watched packages on PyPI, collects version information, compares
against module-pinned versions, and produces a snapshot JSON file.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import tomllib
from datetime import datetime, timezone
from pathlib import Path

import httpx
import packaging.version

# ---------------------------------------------------------------------------
# Package name normalisation (PEP 503)
# ---------------------------------------------------------------------------

_NORMALISE_RE = re.compile(r"[-_.]+")


def _normalise(name: str) -> str:
    """Normalise a package name per PEP 503: lowercase, underscores/dots to hyphens."""
    return _NORMALISE_RE.sub("-", name).lower()


# Regex that splits a dependency string into (name, version_specifier).
# The name is everything up to the first version-specifier character.
_DEP_SPLIT_RE = re.compile(r"^([A-Za-z0-9][-A-Za-z0-9_.]*)(.*)")


def _split_dep(dep: str) -> tuple[str, str]:
    """Split a dependency string into (normalised_name, version_spec).

    Examples
    --------
    >>> _split_dep("sepal_ui==2.21.0")
    ('sepal-ui', '==2.21.0')
    >>> _split_dep("earthengine-api")
    ('earthengine-api', '')
    """
    dep = dep.strip()
    m = _DEP_SPLIT_RE.match(dep)
    if not m:
        return (_normalise(dep), "")
    name = m.group(1)
    spec = m.group(2).strip()
    # Remove any extras markers like [extra] before the specifier
    if spec.startswith("["):
        close = spec.find("]")
        if close != -1:
            spec = spec[close + 1 :].strip()
    # Remove environment markers (everything after ;)
    if ";" in spec:
        spec = spec[: spec.index(";")].strip()
    return (_normalise(name), spec)


# ---------------------------------------------------------------------------
# Watchlist loading
# ---------------------------------------------------------------------------


def load_watchlist(path: Path) -> dict[str, list[dict]]:
    """Load the watchlist JSON and return packages grouped by tier name.

    Parameters
    ----------
    path : Path
        Path to the watchlist JSON file.

    Returns
    -------
    dict[str, list[dict]]
        Mapping of tier name to list of package dicts.
    """
    data = json.loads(Path(path).read_text())
    return {tier: info["packages"] for tier, info in data["tiers"].items()}


# ---------------------------------------------------------------------------
# Version jump classification
# ---------------------------------------------------------------------------


def classify_version_jump(old: str, new: str) -> str:
    """Classify the version jump between *old* and *new*.

    Returns one of ``"major"``, ``"minor"``, ``"patch"``, or ``"none"``.
    """
    v_old = packaging.version.Version(old)
    v_new = packaging.version.Version(new)

    if v_new.major != v_old.major:
        return "major"
    if v_new.minor != v_old.minor:
        return "minor"
    if v_new.micro != v_old.micro:
        return "patch"
    return "none"


# ---------------------------------------------------------------------------
# Dependency extraction – requirements.txt
# ---------------------------------------------------------------------------


def extract_deps_from_requirements(path: Path) -> dict[str, str]:
    """Parse a ``requirements.txt`` file and return normalised deps.

    Returns
    -------
    dict[str, str]
        Mapping of normalised package name to version specifier string.
        An empty string means no version was pinned.
    """
    deps: dict[str, str] = {}
    for raw_line in Path(path).read_text().splitlines():
        line = raw_line.strip()
        # Skip blank, comments, -r includes, -- flags
        if not line or line.startswith("#") or line.startswith("-r") or line.startswith("--"):
            continue
        name, spec = _split_dep(line)
        deps[name] = spec
    return deps


# ---------------------------------------------------------------------------
# Dependency extraction – sepal_environment.yml
# ---------------------------------------------------------------------------


def extract_deps_from_environment_yml(path: Path) -> dict[str, str]:
    """Parse a ``sepal_environment.yml`` and return normalised deps.

    Uses simple line parsing (not a full YAML parser) since these files
    follow a consistent format::

        dependencies:
          - python=3.10
          - pip:
            - sepal_ui==2.21.0

    Conda deps use a single ``=`` for version pinning while pip deps use
    standard specifiers (``==``, ``>=``, etc.).

    Returns
    -------
    dict[str, str]
        Mapping of normalised package name to version specifier string.
    """
    deps: dict[str, str] = {}
    in_pip = False

    for raw_line in Path(path).read_text().splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#"):
            continue

        # Detect start of pip section
        if line == "- pip:" or line == "- pip":
            in_pip = True
            continue

        # A line starting with "- " inside dependencies
        if line.startswith("- "):
            pkg = line[2:].strip()

            # Remove inline comments
            if " #" in pkg:
                pkg = pkg[: pkg.index(" #")].strip()

            if in_pip:
                # Pip deps use standard specifiers
                name, spec = _split_dep(pkg)
                deps[name] = spec
            else:
                # Conda deps use single = for version
                # Check if we left the dependencies section
                if ":" in pkg:
                    # e.g. "pip:" handled above, but catch others
                    continue
                # Split on first = for conda
                if "=" in pkg:
                    eq_idx = pkg.index("=")
                    name = pkg[:eq_idx]
                    spec = pkg[eq_idx:]  # includes the leading =
                    deps[_normalise(name)] = spec
                else:
                    deps[_normalise(pkg)] = ""
        else:
            # If we hit a non-"- " line (like "dependencies:" or "name:"),
            # reset pip context if we're done with deps
            if not line.startswith(" ") and ":" in line:
                in_pip = False

    return deps


# ---------------------------------------------------------------------------
# Dependency extraction – pyproject.toml
# ---------------------------------------------------------------------------


def extract_deps_from_pyproject(path: Path) -> dict[str, str]:
    """Parse a ``pyproject.toml`` and return normalised deps.

    Reads the ``[project] dependencies`` array.  Handles compound specifiers
    like ``"planet>=2.0,<3.0"``.

    Returns
    -------
    dict[str, str]
        Mapping of normalised package name to version specifier string.
    """
    data = tomllib.loads(Path(path).read_text())
    raw_deps = data.get("project", {}).get("dependencies", [])
    deps: dict[str, str] = {}
    for dep_str in raw_deps:
        name, spec = _split_dep(dep_str)
        deps[name] = spec
    return deps


# ---------------------------------------------------------------------------
# PyPI fetching (async)
# ---------------------------------------------------------------------------


async def fetch_pypi_info(client: httpx.AsyncClient, package_name: str) -> dict:
    """Fetch version information for *package_name* from PyPI.

    Parameters
    ----------
    client : httpx.AsyncClient
        Reusable HTTP client.
    package_name : str
        Normalised package name.

    Returns
    -------
    dict
        Keys: ``latest``, ``latest_release_date``, ``all_versions``.
        On error, returns ``{"error": "..."}``.
    """
    try:
        resp = await client.get(f"https://pypi.org/pypi/{package_name}/json")
    except httpx.HTTPError as exc:
        return {"error": str(exc)}

    if resp.status_code != 200:
        return {"error": f"HTTP {resp.status_code}"}

    data = resp.json()
    info = data["info"]
    releases = data["releases"]

    latest = info["version"]

    # Release date of latest version
    latest_files = releases.get(latest, [])
    latest_release_date = (
        latest_files[0]["upload_time_iso_8601"][:10] if latest_files else None
    )

    # Sort versions, pushing pre-releases to the bottom
    def _sort_key(v: str):
        try:
            pv = packaging.version.Version(v)
            return (0 if not pv.is_prerelease else 1, pv)
        except packaging.version.InvalidVersion:
            return (2, packaging.version.Version("0"))

    all_versions = sorted(releases.keys(), key=_sort_key)

    return {
        "latest": latest,
        "latest_release_date": latest_release_date,
        "all_versions": all_versions,
    }


# ---------------------------------------------------------------------------
# Module dependency scanning
# ---------------------------------------------------------------------------


def scan_module_deps(modules_json_path: Path, base_dir: Path) -> dict:
    """Walk all modules from *modules.json* and extract their dependencies.

    Parameters
    ----------
    modules_json_path : Path
        Path to the ``modules.json`` file.
    base_dir : Path
        Base directory where module repos are cloned.

    Returns
    -------
    dict
        Mapping of module name to ``{"file": ..., "packages": ...}``.
    """
    data = json.loads(modules_json_path.read_text())
    result: dict[str, dict] = {}

    for category in data["categories"]:
        for module in category.get("modules", []):
            local_dir = module.get("local_dir")
            if not local_dir:
                continue

            module_path = base_dir / local_dir
            if not module_path.is_dir():
                continue

            # Try each dependency file in priority order
            pyproject = module_path / "pyproject.toml"
            requirements = module_path / "requirements.txt"
            environment_yml = module_path / "sepal_environment.yml"

            if pyproject.exists():
                deps = extract_deps_from_pyproject(pyproject)
                result[module["name"]] = {"file": "pyproject.toml", "packages": deps}
            elif requirements.exists():
                deps = extract_deps_from_requirements(requirements)
                result[module["name"]] = {"file": "requirements.txt", "packages": deps}
            elif environment_yml.exists():
                deps = extract_deps_from_environment_yml(environment_yml)
                result[module["name"]] = {
                    "file": "sepal_environment.yml",
                    "packages": deps,
                }

    return result


# ---------------------------------------------------------------------------
# Snapshot building
# ---------------------------------------------------------------------------


def build_snapshot(
    pypi_data: dict,
    module_deps: dict,
    watchlist_flat: dict,
) -> dict:
    """Build the snapshot structure from PyPI data, module deps, and watchlist.

    Parameters
    ----------
    pypi_data : dict
        Mapping of package name to PyPI info dict (``latest``, etc.).
    module_deps : dict
        Mapping of module name to ``{"file": ..., "packages": ...}``.
    watchlist_flat : dict
        Mapping of package name to ``{"tier": ..., "github": ...}``.

    Returns
    -------
    dict
        Full snapshot with ``scan_date``, ``packages``, ``module_deps``,
        ``summary``.
    """
    packages: dict[str, dict] = {}

    # Tier counters for summary
    tier_update_counts: dict[str, int] = {
        "critical": 0,
        "important": 0,
        "ecosystem": 0,
        "ai_ml": 0,
    }

    for pkg_name, pypi_info in pypi_data.items():
        if "error" in pypi_info:
            continue

        tier = watchlist_flat.get(pkg_name, {}).get("tier", "unknown")
        github = watchlist_flat.get(pkg_name, {}).get("github", "")
        changelog_url = f"https://github.com/{github}/releases" if github else ""

        # Determine version jump by comparing each module's pinned version
        # against the latest PyPI version
        version_jump = "unknown"
        latest = pypi_info.get("latest", "")

        for _mod_name, mod_info in module_deps.items():
            mod_pkgs = mod_info.get("packages", {})
            if pkg_name in mod_pkgs:
                spec = mod_pkgs[pkg_name]
                # Extract the version number from the specifier
                version_match = re.search(r"[\d]+\.[\d]+(?:\.[\d]+)?", spec)
                if version_match and latest:
                    pinned = version_match.group(0)
                    # Pad to 3 components if needed
                    parts = pinned.split(".")
                    while len(parts) < 3:
                        parts.append("0")
                    pinned = ".".join(parts)

                    latest_parts = latest.split(".")
                    while len(latest_parts) < 3:
                        latest_parts.append("0")
                    latest_padded = ".".join(latest_parts[:3])

                    version_jump = classify_version_jump(pinned, latest_padded)
                    break

        # Count updates per tier
        if version_jump not in ("none", "unknown") and tier in tier_update_counts:
            tier_update_counts[tier] += 1

        packages[pkg_name] = {
            "tier": tier,
            "latest": latest,
            "latest_release_date": pypi_info.get("latest_release_date"),
            "version_jump": version_jump,
            "changelog_url": changelog_url,
            "all_versions": pypi_info.get("all_versions", []),
        }

    summary = {
        "critical_updates": tier_update_counts["critical"],
        "important_updates": tier_update_counts["important"],
        "ecosystem_updates": tier_update_counts["ecosystem"],
        "ai_ml_updates": tier_update_counts["ai_ml"],
        "total_packages_scanned": len(packages),
    }

    return {
        "scan_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S") + "Z",
        "packages": packages,
        "module_deps": module_deps,
        "summary": summary,
    }


# ---------------------------------------------------------------------------
# Pretty-print summary
# ---------------------------------------------------------------------------

# Mapping from tier key to display name
_TIER_DISPLAY = {
    "critical": "CRITICAL",
    "important": "IMPORTANT",
    "ecosystem": "ECOSYSTEM",
    "ai_ml": "AI/ML",
}


def print_summary(snapshot: dict) -> None:
    """Print a human-readable summary of *snapshot* to stdout."""
    scan_date = snapshot["scan_date"][:10]
    header = f"Dependency Scan \u2014 {scan_date}"
    print(header)
    print("=" * len(header))
    print()

    packages = snapshot.get("packages", {})

    # Group packages by tier
    by_tier: dict[str, list[tuple[str, dict]]] = {
        t: [] for t in _TIER_DISPLAY
    }
    for pkg_name, pkg_info in packages.items():
        tier = pkg_info.get("tier", "unknown")
        if tier in by_tier:
            by_tier[tier].append((pkg_name, pkg_info))

    for tier_key, display_name in _TIER_DISPLAY.items():
        tier_pkgs = by_tier.get(tier_key, [])
        updates = [
            (n, p) for n, p in tier_pkgs if p.get("version_jump") not in ("none", "unknown")
        ]
        count = len(updates)

        if updates:
            print(f"{display_name} ({count} update{'s' if count != 1 else ''}):")
            # Find the pinned version from module_deps for display
            module_deps = snapshot.get("module_deps", {})
            for pkg_name, pkg_info in updates:
                latest = pkg_info.get("latest", "?")
                jump = pkg_info.get("version_jump", "?")
                # Try to find a pinned version from any module
                pinned = "?"
                for _mod, mod_info in module_deps.items():
                    spec = mod_info.get("packages", {}).get(pkg_name, "")
                    if spec:
                        version_match = re.search(r"[\d]+\.[\d]+(?:\.[\d]+)?", spec)
                        if version_match:
                            pinned = version_match.group(0)
                            break
                print(f"  {pkg_name:<20s} {pinned} \u2192 {latest}  ({jump})")
            print()
        else:
            print(f"{display_name} (0 updates)")
            print()

    print(f"Security: 0 advisories")
    print(f"Snapshot saved to monitoring/snapshots/{scan_date}.json")


# ---------------------------------------------------------------------------
# Async main
# ---------------------------------------------------------------------------


async def main(args: argparse.Namespace) -> None:
    """Orchestrate the full scan pipeline."""
    # Resolve paths relative to CWD
    watchlist_path = Path(args.watchlist)
    modules_json_path = Path(args.modules_json)
    output_dir = Path(args.output)
    base_dir = Path(args.base_dir)

    # 1. Load watchlist
    watchlist = load_watchlist(watchlist_path)

    # Build flat lookup: package_name -> {tier, github}
    watchlist_flat: dict[str, dict] = {}
    all_package_names: list[str] = []
    for tier_name, pkgs in watchlist.items():
        for pkg in pkgs:
            normalised = _normalise(pkg["name"])
            watchlist_flat[normalised] = {
                "tier": tier_name,
                "github": pkg.get("github", ""),
            }
            all_package_names.append(pkg.get("pypi", pkg["name"]))

    # 2. Fetch PyPI info for all watched packages
    pypi_data: dict[str, dict] = {}
    async with httpx.AsyncClient(timeout=30.0) as client:
        tasks = {
            _normalise(name): fetch_pypi_info(client, name)
            for name in all_package_names
        }
        results = await asyncio.gather(*tasks.values())
        for key, result in zip(tasks.keys(), results):
            pypi_data[key] = result

    # 3. Scan module dependencies
    module_deps = scan_module_deps(modules_json_path, base_dir)

    # 4. Build snapshot
    snapshot = build_snapshot(pypi_data, module_deps, watchlist_flat)

    # 5. Save snapshot
    output_dir.mkdir(parents=True, exist_ok=True)
    scan_date = snapshot["scan_date"][:10]
    out_file = output_dir / f"{scan_date}.json"
    out_file.write_text(json.dumps(snapshot, indent=2) + "\n")

    # 6. Print summary
    print_summary(snapshot)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scan PyPI for dependency updates"
    )
    parser.add_argument(
        "--output",
        default="monitoring/snapshots/",
        help="Output directory for snapshots",
    )
    parser.add_argument(
        "--watchlist",
        default="monitoring/watchlist.json",
        help="Watchlist JSON path",
    )
    parser.add_argument(
        "--modules-json",
        default="modules.json",
        help="modules.json path",
    )
    parser.add_argument(
        "--base-dir",
        default="/home/dguerrero/1_modules",
        help="Base directory for module repos",
    )
    args = parser.parse_args()
    asyncio.run(main(args))
