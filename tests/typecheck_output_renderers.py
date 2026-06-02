from __future__ import annotations

from rich_toolkit import RichToolkit


class Deployment:
    id = "dep_123"


class Project:
    id = "proj_123"


def render_deployment(deployment: Deployment) -> str:
    return deployment.id


def render_deployment_with_toolkit(
    deployment: Deployment, toolkit: RichToolkit
) -> None:
    toolkit.print(deployment.id)


def render_project(project: Project) -> str:
    return project.id


app = RichToolkit()
app.output(Deployment(), render_output=render_deployment)
app.output(Deployment(), render_output=render_deployment_with_toolkit)
app.output(Deployment(), render_output=render_project)  # type: ignore[arg-type]  # ty: ignore[no-matching-overload]
