"""Tests for check_deps.py scanner."""

import json
from pathlib import Path

import pytest


def test_load_watchlist(tmp_path):
    """Watchlist loads and returns packages grouped by tier."""
    watchlist = {
        "meta": {"last_scan": None, "scan_frequency": "weekly"},
        "tiers": {
            "critical": {
                "description": "test",
                "packages": [
                    {"name": "solara", "pypi": "solara", "github": "widgetti/solara", "reason": "framework"}
                ],
            }
        },
    }
    wl_path = tmp_path / "watchlist.json"
    wl_path.write_text(json.dumps(watchlist))

    from scripts.check_deps import load_watchlist

    result = load_watchlist(wl_path)
    assert "critical" in result
    assert result["critical"][0]["name"] == "solara"


def test_parse_version_jump():
    """Version jump classification works correctly."""
    from scripts.check_deps import classify_version_jump

    assert classify_version_jump("1.0.0", "2.0.0") == "major"
    assert classify_version_jump("1.0.0", "1.1.0") == "minor"
    assert classify_version_jump("1.0.0", "1.0.1") == "patch"
    assert classify_version_jump("1.0.0", "1.0.0") == "none"


def test_classify_version_jump_prerelease():
    """Pre-release versions are handled."""
    from scripts.check_deps import classify_version_jump

    assert classify_version_jump("1.0.0", "1.0.1a1") == "patch"
    assert classify_version_jump("1.0.0", "2.0.0rc1") == "major"


def test_extract_module_deps(tmp_path):
    """Extract pinned versions from a module's requirements.txt."""
    req = tmp_path / "requirements.txt"
    req.write_text("sepal_ui==2.21.0\nearthengine-api\nrasterio<=1.4.3\n")

    from scripts.check_deps import extract_deps_from_requirements

    deps = extract_deps_from_requirements(req)
    assert deps["sepal-ui"] == "==2.21.0"
    assert deps["earthengine-api"] == ""
    assert deps["rasterio"] == "<=1.4.3"


def test_extract_module_deps_yml(tmp_path):
    """Extract pinned versions from sepal_environment.yml."""
    yml = tmp_path / "sepal_environment.yml"
    yml.write_text(
        "dependencies:\n"
        "  - python=3.10\n"
        "  - gdal=3.8.3\n"
        "  - pip:\n"
        "    - sepal_ui==2.21.0\n"
        "    - earthengine-api\n"
    )

    from scripts.check_deps import extract_deps_from_environment_yml

    deps = extract_deps_from_environment_yml(yml)
    assert deps["python"] == "=3.10"
    assert deps["gdal"] == "=3.8.3"
    assert deps["sepal-ui"] == "==2.21.0"


def test_extract_deps_from_pyproject(tmp_path):
    """Extract dependencies from pyproject.toml."""
    toml = tmp_path / "pyproject.toml"
    toml.write_text(
        '[project]\n'
        'name = "test"\n'
        'dependencies = [\n'
        '    "solara",\n'
        '    "geopandas>=0.14.0",\n'
        '    "earthengine-api>1.6.0",\n'
        '    "planet>=2.0,<3.0",\n'
        ']\n'
    )

    from scripts.check_deps import extract_deps_from_pyproject

    deps = extract_deps_from_pyproject(toml)
    assert deps["solara"] == ""
    assert deps["geopandas"] == ">=0.14.0"
    assert deps["earthengine-api"] == ">1.6.0"
    assert deps["planet"] == ">=2.0,<3.0"


def test_build_snapshot_structure():
    """Snapshot has the expected top-level keys."""
    from scripts.check_deps import build_snapshot

    pypi_data = {
        "solara": {
            "latest": "1.44.0",
            "latest_release_date": "2026-02-20",
            "all_versions": ["1.42.0", "1.43.0", "1.44.0"],
        }
    }
    module_deps = {
        "sepal_ui": {"file": "pyproject.toml", "packages": {"solara": ">=1.0"}},
    }
    watchlist_flat = {
        "solara": {"tier": "critical", "github": "widgetti/solara"},
    }

    snapshot = build_snapshot(pypi_data, module_deps, watchlist_flat)
    assert "scan_date" in snapshot
    assert "packages" in snapshot
    assert "module_deps" in snapshot
    assert "summary" in snapshot
    assert snapshot["packages"]["solara"]["tier"] == "critical"
    assert snapshot["packages"]["solara"]["latest"] == "1.44.0"
