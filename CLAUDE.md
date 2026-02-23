# CLAUDE.md — SEPAL Module Migration Orchestrator

This file is auto-generated from `modules.json` using `scripts/generate_claude_md.py`.
Do **not** edit directly — your changes will be overwritten.

## Purpose

This repository orchestrates the migration of SEPAL modules from Jupyter/ipyleaflet/voila to pure Solara apps. It tracks migration status, complexity, blockers, and session history for 22 Jupyter/Conda modules.

## Status Dashboard

| # | Module | Status | Complexity | Last Session |
|---|--------|--------|------------|--------------|
| 1 | [sepal_pysmm](https://github.com/sepal-contrib/sepal_pysmm) | audited | high | 2026-02-23 |
| 2 | [gfc_wrapper_python](https://github.com/sepal-contrib/gfc_wrapper_python) | audited | medium | 2026-02-23 |
| 3 | [vector_manager](https://github.com/sepal-contrib/vector_manager) | audited | medium | 2026-02-23 |
| 4 | [clip-time-series](https://github.com/sepal-contrib/clip-time-series) | audited | medium | 2026-02-23 |
| 5 | [alos_mosaics](https://github.com/sepal-contrib/alos_mosaics) | audited | medium | 2026-02-23 |
| 6 | [sdg_15.3.1](https://github.com/sepal-contrib/sdg_15.3.1) | audited | high | 2026-02-23 |
| 7 | [tmf_sepal](https://github.com/sepal-contrib/tmf_sepal) | audited | low | 2026-02-23 |
| 8 | [planet-order](https://github.com/sepal-contrib/planet-order) | audited | medium | 2026-02-23 |
| 9 | [coverage_analysis](https://github.com/sepal-contrib/coverage_analysis) | audited | medium | 2026-02-23 |
| 10 | [fcdm](https://github.com/sepal-contrib/fcdm) | audited | high | 2026-02-23 |
| 11 | [basin-rivers](https://github.com/sepal-contrib/basin-rivers) | audited | medium | 2026-02-23 |
| 12 | [gee_source](https://github.com/sepal-contrib/gee_source) | audited | low | 2026-02-23 |
| 13 | [active_fires_explorer](https://github.com/sepal-contrib/planet_active_fires_explorer) | audited | medium | 2026-02-23 |
| 14 | [sepal_smfm_biota](https://github.com/sepal-contrib/sepal_smfm_biota) | audited | low | 2026-02-23 |
| 15 | [smfm_deforest](https://github.com/smfm-project/deforest) | skip | — | — |
| 16 | [gwb](https://github.com/sepal-contrib/gwb) | audited | high | 2026-02-23 |
| 17 | [cumsum_change](https://github.com/sepal-contrib/cumsum_change) | audited | medium | 2026-02-23 |
| 18 | [weplan](https://github.com/sepal-contrib/weplan) | audited | medium | 2026-02-23 |
| 19 | [sepal-leafmap](https://github.com/sepal-contrib/sepal-leafmap) | audited | low | 2026-02-23 |
| 20 | [eSBAE_notebooks](https://github.com/sepal-contrib/eSBAE_notebooks) | audited | low | 2026-02-23 |
| 21 | [deforestation-alerts](https://github.com/sepal-contrib/deforestation-alerts-module) | audited | high | 2026-02-23 |
| 22 | [sbae-design](https://github.com/sepal-contrib/sbae-design) | done | — | — |


## Summary

- **Done**: 1
- **In Progress**: 0
- **Audited**: 20
- **Blocked**: 0
- **Skip**: 1
- **Not Started**: 0

## Reference Architecture (sbae-design)

Target pattern for all migrated modules:

```python
# app.py — Entry point
import solara
from sepal_ui.sepalwidgets.vue_app import MapApp, ThemeToggle
from sepal_ui.solara import setup_sessions, setup_solara_server, setup_theme_colors

setup_solara_server()

@solara.lab.on_kernel_start
def on_kernel_start():
    return setup_sessions()

@solara.component
def Page():
    setup_theme_colors()
    theme_toggle = ThemeToggle()

    steps_data = [
        {"id": 1, "name": "Step Name", "icon": "mdi-icon", "display": "step", "content": [TileWidget()]},
        # ... more steps
    ]

    MapApp.element(
        app_title="Module Title",
        app_icon="mdi-icon",
        main_map=[map_widget],
        steps_data=steps_data,
        theme_toggle=[theme_toggle],
    )

routes = [solara.Route(path="/", component=Page, label="App")]
```

Key patterns:
- **Entry point**: `app.py` with `@solara.component def Page()`
- **Layout**: `MapApp.element(...)` from sepal_ui
- **Session**: `setup_sessions()` + `@solara.lab.on_kernel_start`
- **Theme**: `ThemeToggle` + `setup_theme_colors()`
- **Components**: `component/{config,model,tile,widget,scripts}/`
- **Dev server**: `solara run app.py --port 8901`

## Workflow: Migrating a Module

### 1. Pick next module
Choose the next `not_started` or `audited` module by priority (low complexity first).

### 2. Open session in the module repo
```bash
cd /home/dguerrero/1_modules/{local_dir}
```
The repo's `CLAUDE.md` contains the full assessment and migration playbook.

### 3. Execute migration
Follow the per-repo CLAUDE.md migration plan step by step.

### 4. Update status
After the session, update `modules.json`:
- Set `migration.status` to the new status
- Set `migration.last_session_date` to today's date
- Write a brief `migration.last_session_summary`
- Update `migration.complexity` if reassessed

### 5. Regenerate
```bash
cd /home/dguerrero/1_modules/module_monitor
uv run python scripts/generate_claude_md.py
uv run python scripts/generate_readme.py
```



## Key Files

| File | Role |
|------|------|
| `modules.json` | Source of truth — migration metadata per module |
| `scripts/generate_claude_md.py` | Generates this CLAUDE.md from modules.json |
| `scripts/generate_readme.py` | Generates README.rst from modules.json |
| `scripts/CLAUDE_MASTER.md.j2` | Jinja2 template for this file |
| `scripts/README.rst.j2` | Jinja2 template for README.rst |

## Module Directories

All repos are cloned at `/home/dguerrero/1_modules/`. Each migrating module has a `CLAUDE.md` with its specific assessment and playbook.

- `sepal_pysmm/` — sepal_pysmm (audited)
- `gfc_wrapper_python/` — gfc_wrapper_python (audited)
- `vector_manager/` — vector_manager (audited)
- `clip-time-series/` — clip-time-series (audited)
- `alos_mosaics/` — alos_mosaics (audited)
- `sdg_15.3.1/` — sdg_15.3.1 (audited)
- `tmf_sepal/` — tmf_sepal (audited)
- `planet-order/` — planet-order (audited)
- `coverage_analysis/` — coverage_analysis (audited)
- `fcdm/` — fcdm (audited)
- `basin-rivers/` — basin-rivers (audited)
- `gee_source/` — gee_source (audited)
- `active-fires-explorer/` — active_fires_explorer (audited)
- `sepal_smfm_biota/` — sepal_smfm_biota (audited)
- `gwb/` — gwb (audited)
- `cumsum_change/` — cumsum_change (audited)
- `weplan/` — weplan (audited)
- `sepal-leafmap/` — sepal-leafmap (audited)
- `eSBAE_notebooks/` — eSBAE_notebooks (audited)
- `deforestation-alerts-module/` — deforestation-alerts (audited)
- `sbae-design/` — sbae-design (done)

