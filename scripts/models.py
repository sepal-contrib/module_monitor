"""Pydantic models for the SEPAL /api/apps/list endpoint."""

from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


class AppEndpoint(str, Enum):
    jupyter = "jupyter"
    docker = "docker"
    shiny = "shiny"
    rstudio = "rstudio"


class AppTag(str, Enum):
    CLASSIFICATION = "CLASSIFICATION"
    DISASTER = "DISASTER"
    PLANET = "PLANET"
    RESTORATION = "RESTORATION"
    SMFM = "SMFM"
    TIME_SERIES = "TIME_SERIES"
    TOOLS = "TOOLS"


class SepalApp(BaseModel):
    """A single app entry from the SEPAL server API."""

    id: str
    label: str
    path: str
    endpoint: AppEndpoint | None = None
    tags: list[AppTag] = []
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
    """Response from /api/apps/list."""

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
