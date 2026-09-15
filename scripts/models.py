"""Pydantic models for a sepal-apps-catalog file (apps.{dev,test,prod}.json).

The same shape is served by SEPAL's /api/apps/list, which app-manager renders
from these files at runtime.
"""

from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


class AppEndpoint(str, Enum):
    jupyter = "jupyter"
    docker = "docker"
    shiny = "shiny"
    rstudio = "rstudio"


class SepalApp(BaseModel):
    """A single app entry in the catalog."""

    id: str
    label: str
    path: str
    endpoint: AppEndpoint | None = None
    # Free-form on purpose: the catalog owns the tag vocabulary and adds to it
    # (FOREST, INSTANT, LAND_COVER and SAR all post-date this model). A closed
    # enum here would reject a valid catalog. check_server_apps.py reports tags
    # an app uses that the catalog itself never declares.
    tags: list[str] = []
    pinned: bool = False
    hidden: bool = False
    single: bool = False
    google_account_required: bool = Field(False, alias="googleAccountRequired")
    logo_ref: str = Field("sepal.png", alias="logoRef")
    author: str = ""
    description: str = ""
    tagline: str = ""
    project_link: str = Field("", alias="projectLink")
    repository: str | None = None
    branch: str | None = None
    port: int | None = None

    model_config = {"populate_by_name": True}


class SepalAppList(BaseModel):
    """A whole catalog file."""

    apps: list[SepalApp]

    def by_repo(self) -> dict[str, SepalApp]:
        """Index apps by their repository URL (only those that have one)."""
        return {app.repository: app for app in self.apps if app.repository}


class DeployStatus(str, Enum):
    """Deployment status of a module on a SEPAL server."""

    active = "active"
    hidden = "hidden"
    missing = "missing"


def get_deploy_status(app: SepalApp | None) -> DeployStatus:
    """Determine the deployment status from an app entry."""
    if app is None:
        return DeployStatus.missing
    return DeployStatus.hidden if app.hidden else DeployStatus.active
