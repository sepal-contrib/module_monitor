Core Library
============

+----+-----------------------------+------------------------------------------------------------------------------------------------------+------+------+
| #  | Module name                 | Status                                                                                               | prod | test |
+====+=============================+======================================================================================================+======+======+
| 1  | `sepal_ui`_                 | |sepal_ui_unit_badge|_                                                                               |      |      |
|    |                             |                                                                                                      |      |      |
|    |                             |                                                                                                      |      |      |
+----+-----------------------------+------------------------------------------------------------------------------------------------------+------+------+


Solara Modules
==============

+----+-----------------------------+------------------------------------------------------------------------------------------------------+------+------+
| #  | Module name                 | Status                                                                                               | prod | test |
+====+=============================+======================================================================================================+======+======+
| 1  | `se.plan`_                  |                                                                                                      | ✓    | ✓    |
|    |                             |                                                                                                      |      |      |
|    |                             |                                                                                                      |      |      |
+----+-----------------------------+------------------------------------------------------------------------------------------------------+------+------+
| 2  | `sepal_mgci`_               |                                                                                                      | ✓    | ✓    |
|    |                             |                                                                                                      |      |      |
|    |                             |                                                                                                      |      |      |
+----+-----------------------------+------------------------------------------------------------------------------------------------------+------+------+
| 3  | `sepal-gee-bundle`_         |                                                                                                      |      |      |
|    |                             |                                                                                                      |      |      |
|    |                             |                                                                                                      |      |      |
+----+-----------------------------+------------------------------------------------------------------------------------------------------+------+------+


Jupyter/Conda Modules
=====================

+----+-----------------------------+------------------------------------------------------------------------------------------------------+------+------+-----------+--------------------------------+------------------------------------------------------+
| #  | Module name                 | Status                                                                                               | prod | test | conda env | migration                      | comments                                             |
+====+=============================+======================================================================================================+======+======+===========+================================+======================================================+
| 1  | `sepal_pysmm`_              | |sepal_pysmm_ci_badge|_                                                                              | ✓    | ✓    | yes       | audited                        |                                                      |
+----+-----------------------------+------------------------------------------------------------------------------------------------------+------+------+-----------+--------------------------------+------------------------------------------------------+
| 2  | `gfc_wrapper_python`_       | |gfc_wrapper_python_ci_badge|_                                                                       | ✓    | ✓    | yes       | done → /gfc                    | Lives in sepal-gee-bundle at /gfc                    |
+----+-----------------------------+------------------------------------------------------------------------------------------------------+------+------+-----------+--------------------------------+------------------------------------------------------+
| 3  | `vector_manager`_           | |vector_manager_ci_badge|_                                                                           | ✓    | ✓    | yes       | audited                        |                                                      |
+----+-----------------------------+------------------------------------------------------------------------------------------------------+------+------+-----------+--------------------------------+------------------------------------------------------+
| 4  | `clip-time-series`_         | |clip_time_series_ci_badge|_                                                                         | ✓    | ✓    | yes       | audited                        |                                                      |
+----+-----------------------------+------------------------------------------------------------------------------------------------------+------+------+-----------+--------------------------------+------------------------------------------------------+
| 5  | `alos_mosaics`_             | |alos_mosaics_ci_badge|_                                                                             | ✓    | ✓    | yes       | done → /alos-mosaics           | Lives in sepal-gee-bundle at /alos-mosaics           |
+----+-----------------------------+------------------------------------------------------------------------------------------------------+------+------+-----------+--------------------------------+------------------------------------------------------+
| 6  | `sdg_15.3.1`_               | |sdg_15_3_1_ci_badge|_                                                                               | ✓    | ✓    | yes       | audited                        |                                                      |
+----+-----------------------------+------------------------------------------------------------------------------------------------------+------+------+-----------+--------------------------------+------------------------------------------------------+
| 7  | `tmf_sepal`_                | |tmf_sepal_ci_badge|_                                                                                | ✓    | ✓    | yes       | done → /tmf-sepal              | Lives in sepal-gee-bundle at /tmf-sepal              |
+----+-----------------------------+------------------------------------------------------------------------------------------------------+------+------+-----------+--------------------------------+------------------------------------------------------+
| 8  | `planet-order`_             | |planet_order_ci_badge|_                                                                             | ✓    | ✓    | yes       | audited                        |                                                      |
+----+-----------------------------+------------------------------------------------------------------------------------------------------+------+------+-----------+--------------------------------+------------------------------------------------------+
| 9  | `coverage_analysis`_        | |coverage_analysis_ci_badge|_                                                                        | ✓    | ✓    | yes       | done → /coverage-analysis      | Lives in sepal-gee-bundle at /coverage-analysis      |
+----+-----------------------------+------------------------------------------------------------------------------------------------------+------+------+-----------+--------------------------------+------------------------------------------------------+
| 10 | `fcdm`_                     | |fcdm_ci_badge|_                                                                                     | ✓    | ✓    | yes       | done → /fcdm                   | Lives in sepal-gee-bundle at /fcdm                   |
+----+-----------------------------+------------------------------------------------------------------------------------------------------+------+------+-----------+--------------------------------+------------------------------------------------------+
| 11 | `basin-rivers`_             | |basin_rivers_ci_badge|_                                                                             | ✓    | ✓    | yes       | done → /basin-rivers           | Lives in sepal-gee-bundle at /basin-rivers           |
+----+-----------------------------+------------------------------------------------------------------------------------------------------+------+------+-----------+--------------------------------+------------------------------------------------------+
| 12 | `gee_source`_               | |gee_source_ci_badge|_                                                                               | ✓    | ✓    | yes       | done → /gee-source             | Lives in sepal-gee-bundle at /gee-source             |
+----+-----------------------------+------------------------------------------------------------------------------------------------------+------+------+-----------+--------------------------------+------------------------------------------------------+
| 13 | `active_fires_explorer`_    | |active_fires_explorer_ci_badge|_                                                                    | ✓    | ✓    | yes       | audited                        |                                                      |
+----+-----------------------------+------------------------------------------------------------------------------------------------------+------+------+-----------+--------------------------------+------------------------------------------------------+
| 14 | `sepal_smfm_biota`_         | |sepal_smfm_biota_ci_badge|_                                                                         | ✓    | ✓    | yes       | audited                        |                                                      |
+----+-----------------------------+------------------------------------------------------------------------------------------------------+------+------+-----------+--------------------------------+------------------------------------------------------+
| 15 | `smfm_deforest`_            |                                                                                                      | ✓    | ✓    | yes       | skip                           | external repo, not cloned locally                    |
+----+-----------------------------+------------------------------------------------------------------------------------------------------+------+------+-----------+--------------------------------+------------------------------------------------------+
| 16 | `gwb`_                      | |gwb_ci_badge|_                                                                                      | ✓    | ✓    | yes       | audited                        |                                                      |
+----+-----------------------------+------------------------------------------------------------------------------------------------------+------+------+-----------+--------------------------------+------------------------------------------------------+
| 17 | `cumsum_change`_            | |cumsum_change_ci_badge|_                                                                            | ✓    | ✓    | yes       | audited                        | Declined for sepal-gee-bundle (local TF/rasterio)    |
+----+-----------------------------+------------------------------------------------------------------------------------------------------+------+------+-----------+--------------------------------+------------------------------------------------------+
| 18 | `weplan`_                   | |weplan_ci_badge|_                                                                                   | ✓    |      | yes       | audited                        | only in prod server                                  |
+----+-----------------------------+------------------------------------------------------------------------------------------------------+------+------+-----------+--------------------------------+------------------------------------------------------+
| 19 | `sepal-leafmap`_            | |sepal_leafmap_ci_badge|_                                                                            | ○    | ✓    | yes       | audited                        |                                                      |
+----+-----------------------------+------------------------------------------------------------------------------------------------------+------+------+-----------+--------------------------------+------------------------------------------------------+
| 20 | `eSBAE_notebooks`_          |                                                                                                      | ○    | ✓    |           | audited                        | notebooks, not a standard module                     |
+----+-----------------------------+------------------------------------------------------------------------------------------------------+------+------+-----------+--------------------------------+------------------------------------------------------+
| 21 | `deforestation-alerts`_     | |deforestation_alerts_ci_badge|_                                                                     | ✓    | ✓    | yes       | audited                        |                                                      |
+----+-----------------------------+------------------------------------------------------------------------------------------------------+------+------+-----------+--------------------------------+------------------------------------------------------+
| 22 | `sbae-design`_              | |sbae_design_ci_badge|_  |sbae_design_unit_badge|_                                                   | ✓    | ✓    | yes       | done                           | reference Solara implementation                      |
+----+-----------------------------+------------------------------------------------------------------------------------------------------+------+------+-----------+--------------------------------+------------------------------------------------------+


Legacy Modules (not in prod/test)
=================================

+----+-----------------------------+------------------------------------------------------------------------------------------------------+------+------+-----------+--------------------------------+------------------------------------------------------+
| #  | Module name                 | Status                                                                                               | prod | test | conda env | migration                      | comments                                             |
+====+=============================+======================================================================================================+======+======+===========+================================+======================================================+
| 1  | `alert_module`_             |                                                                                                      |      |      | yes       |                                |                                                      |
+----+-----------------------------+------------------------------------------------------------------------------------------------------+------+------+-----------+--------------------------------+------------------------------------------------------+
| 2  | `damage_proxy_maps`_        |                                                                                                      | ○    | ○    | yes       |                                |                                                      |
+----+-----------------------------+------------------------------------------------------------------------------------------------------+------+------+-----------+--------------------------------+------------------------------------------------------+
| 3  | `bfast_gpu`_                |                                                                                                      |      |      | yes       |                                |                                                      |
+----+-----------------------------+------------------------------------------------------------------------------------------------------+------+------+-----------+--------------------------------+------------------------------------------------------+



How this README is generated
============================

This file is auto-generated from ``modules.json`` using a Jinja2 template.
Do **not** edit ``README.rst`` directly — your changes will be overwritten.

Setup
-----

.. code-block:: bash

   # Install dependencies (one time)
   uv sync

Editing modules
---------------

1. Edit ``modules.json`` — add, remove, or update module entries.
2. Regenerate:

.. code-block:: bash

   uv run python scripts/generate_readme.py

3. Commit both ``modules.json`` and ``README.rst``.

JSON structure
--------------

Each module entry has:

- ``name``: Module display name (used as RST hyperlink reference)
- ``github_url``: Full GitHub repository URL
- ``badge_workflow`` *(optional)*: Workflow filename, defaults to ``ci.yaml`` for modules with a ``ci`` config, otherwise ``unit.yaml``
- ``conda_env`` *(optional)*: ``"yes"`` if the module has a ``sepal_environment.yml``
- ``comments`` *(optional)*: Free-text notes

Modules are grouped into categories, each with its own table columns.


.. _sepal_ui: https://github.com/openforis/sepal_ui
.. _se.plan: https://github.com/sepal-contrib/se.plan
.. _sepal_mgci: https://github.com/sepal-contrib/sepal_mgci
.. _sepal-gee-bundle: https://github.com/sepal-contrib/sepal-gee-bundle
.. _sepal_pysmm: https://github.com/sepal-contrib/sepal_pysmm
.. _gfc_wrapper_python: https://github.com/sepal-contrib/gfc_wrapper_python
.. _vector_manager: https://github.com/sepal-contrib/vector_manager
.. _clip-time-series: https://github.com/sepal-contrib/clip-time-series
.. _alos_mosaics: https://github.com/sepal-contrib/alos_mosaics
.. _sdg_15.3.1: https://github.com/sepal-contrib/sdg_15.3.1
.. _tmf_sepal: https://github.com/sepal-contrib/tmf_sepal
.. _planet-order: https://github.com/sepal-contrib/planet-order
.. _coverage_analysis: https://github.com/sepal-contrib/coverage_analysis
.. _fcdm: https://github.com/sepal-contrib/fcdm
.. _basin-rivers: https://github.com/sepal-contrib/basin-rivers
.. _gee_source: https://github.com/sepal-contrib/gee_source
.. _active_fires_explorer: https://github.com/sepal-contrib/planet_active_fires_explorer
.. _sepal_smfm_biota: https://github.com/sepal-contrib/sepal_smfm_biota
.. _smfm_deforest: https://github.com/smfm-project/deforest
.. _gwb: https://github.com/sepal-contrib/gwb
.. _cumsum_change: https://github.com/sepal-contrib/cumsum_change
.. _weplan: https://github.com/sepal-contrib/weplan
.. _sepal-leafmap: https://github.com/sepal-contrib/sepal-leafmap
.. _eSBAE_notebooks: https://github.com/sepal-contrib/eSBAE_notebooks
.. _deforestation-alerts: https://github.com/sepal-contrib/deforestation-alerts-module
.. _sbae-design: https://github.com/sepal-contrib/sbae-design
.. _alert_module: https://github.com/sepal-contrib/alert_module
.. _damage_proxy_maps: https://github.com/sepal-contrib/damage_proxy_maps
.. _bfast_gpu: https://github.com/sepal-contrib/bfast_gpu

.. |sepal_ui_unit_badge| image:: https://github.com/openforis/sepal_ui/actions/workflows/unit.yml/badge.svg
   :alt: unit.yml
.. _sepal_ui_unit_badge: https://github.com/openforis/sepal_ui/actions/workflows/unit.yml

.. |sepal_pysmm_ci_badge| image:: https://github.com/sepal-contrib/sepal_pysmm/actions/workflows/ci.yaml/badge.svg
   :alt: ci.yaml
.. _sepal_pysmm_ci_badge: https://github.com/sepal-contrib/sepal_pysmm/actions/workflows/ci.yaml

.. |gfc_wrapper_python_ci_badge| image:: https://github.com/sepal-contrib/gfc_wrapper_python/actions/workflows/ci.yaml/badge.svg
   :alt: ci.yaml
.. _gfc_wrapper_python_ci_badge: https://github.com/sepal-contrib/gfc_wrapper_python/actions/workflows/ci.yaml

.. |vector_manager_ci_badge| image:: https://github.com/sepal-contrib/vector_manager/actions/workflows/ci.yaml/badge.svg
   :alt: ci.yaml
.. _vector_manager_ci_badge: https://github.com/sepal-contrib/vector_manager/actions/workflows/ci.yaml

.. |clip_time_series_ci_badge| image:: https://github.com/sepal-contrib/clip-time-series/actions/workflows/ci.yaml/badge.svg
   :alt: ci.yaml
.. _clip_time_series_ci_badge: https://github.com/sepal-contrib/clip-time-series/actions/workflows/ci.yaml

.. |alos_mosaics_ci_badge| image:: https://github.com/sepal-contrib/alos_mosaics/actions/workflows/ci.yaml/badge.svg
   :alt: ci.yaml
.. _alos_mosaics_ci_badge: https://github.com/sepal-contrib/alos_mosaics/actions/workflows/ci.yaml

.. |sdg_15_3_1_ci_badge| image:: https://github.com/sepal-contrib/sdg_15.3.1/actions/workflows/ci.yaml/badge.svg
   :alt: ci.yaml
.. _sdg_15_3_1_ci_badge: https://github.com/sepal-contrib/sdg_15.3.1/actions/workflows/ci.yaml

.. |tmf_sepal_ci_badge| image:: https://github.com/sepal-contrib/tmf_sepal/actions/workflows/ci.yaml/badge.svg
   :alt: ci.yaml
.. _tmf_sepal_ci_badge: https://github.com/sepal-contrib/tmf_sepal/actions/workflows/ci.yaml

.. |planet_order_ci_badge| image:: https://github.com/sepal-contrib/planet-order/actions/workflows/ci.yaml/badge.svg
   :alt: ci.yaml
.. _planet_order_ci_badge: https://github.com/sepal-contrib/planet-order/actions/workflows/ci.yaml

.. |coverage_analysis_ci_badge| image:: https://github.com/sepal-contrib/coverage_analysis/actions/workflows/ci.yaml/badge.svg
   :alt: ci.yaml
.. _coverage_analysis_ci_badge: https://github.com/sepal-contrib/coverage_analysis/actions/workflows/ci.yaml

.. |fcdm_ci_badge| image:: https://github.com/sepal-contrib/fcdm/actions/workflows/ci.yaml/badge.svg
   :alt: ci.yaml
.. _fcdm_ci_badge: https://github.com/sepal-contrib/fcdm/actions/workflows/ci.yaml

.. |basin_rivers_ci_badge| image:: https://github.com/sepal-contrib/basin-rivers/actions/workflows/ci.yaml/badge.svg
   :alt: ci.yaml
.. _basin_rivers_ci_badge: https://github.com/sepal-contrib/basin-rivers/actions/workflows/ci.yaml

.. |gee_source_ci_badge| image:: https://github.com/sepal-contrib/gee_source/actions/workflows/ci.yaml/badge.svg
   :alt: ci.yaml
.. _gee_source_ci_badge: https://github.com/sepal-contrib/gee_source/actions/workflows/ci.yaml

.. |active_fires_explorer_ci_badge| image:: https://github.com/sepal-contrib/planet_active_fires_explorer/actions/workflows/ci.yaml/badge.svg
   :alt: ci.yaml
.. _active_fires_explorer_ci_badge: https://github.com/sepal-contrib/planet_active_fires_explorer/actions/workflows/ci.yaml

.. |sepal_smfm_biota_ci_badge| image:: https://github.com/sepal-contrib/sepal_smfm_biota/actions/workflows/ci.yaml/badge.svg
   :alt: ci.yaml
.. _sepal_smfm_biota_ci_badge: https://github.com/sepal-contrib/sepal_smfm_biota/actions/workflows/ci.yaml

.. |gwb_ci_badge| image:: https://github.com/sepal-contrib/gwb/actions/workflows/ci.yaml/badge.svg
   :alt: ci.yaml
.. _gwb_ci_badge: https://github.com/sepal-contrib/gwb/actions/workflows/ci.yaml

.. |cumsum_change_ci_badge| image:: https://github.com/sepal-contrib/cumsum_change/actions/workflows/ci.yaml/badge.svg
   :alt: ci.yaml
.. _cumsum_change_ci_badge: https://github.com/sepal-contrib/cumsum_change/actions/workflows/ci.yaml

.. |weplan_ci_badge| image:: https://github.com/sepal-contrib/weplan/actions/workflows/ci.yaml/badge.svg
   :alt: ci.yaml
.. _weplan_ci_badge: https://github.com/sepal-contrib/weplan/actions/workflows/ci.yaml

.. |sepal_leafmap_ci_badge| image:: https://github.com/sepal-contrib/sepal-leafmap/actions/workflows/ci.yaml/badge.svg
   :alt: ci.yaml
.. _sepal_leafmap_ci_badge: https://github.com/sepal-contrib/sepal-leafmap/actions/workflows/ci.yaml

.. |deforestation_alerts_ci_badge| image:: https://github.com/sepal-contrib/deforestation-alerts-module/actions/workflows/ci.yaml/badge.svg
   :alt: ci.yaml
.. _deforestation_alerts_ci_badge: https://github.com/sepal-contrib/deforestation-alerts-module/actions/workflows/ci.yaml

.. |sbae_design_ci_badge| image:: https://github.com/sepal-contrib/sbae-design/actions/workflows/ci.yaml/badge.svg
   :alt: ci.yaml
.. _sbae_design_ci_badge: https://github.com/sepal-contrib/sbae-design/actions/workflows/ci.yaml

.. |sbae_design_unit_badge| image:: https://github.com/sepal-contrib/sbae-design/actions/workflows/unit.yaml/badge.svg
   :alt: unit.yaml
.. _sbae_design_unit_badge: https://github.com/sepal-contrib/sbae-design/actions/workflows/unit.yaml

