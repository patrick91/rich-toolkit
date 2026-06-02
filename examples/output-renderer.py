from __future__ import annotations

import argparse
from typing import Literal

from pydantic import BaseModel

from rich_toolkit import RichToolkit
from rich_toolkit.styles import TaggedStyle


class DeploymentResult(BaseModel):
    id: str
    slug: str
    status: str
    url: str


def render_deployment_output(
    deployment: DeploymentResult, toolkit: RichToolkit
) -> None:
    toolkit.print(deployment.slug, tag="deploy")
    toolkit.print(deployment.status, tag="status")
    toolkit.print(deployment.url, tag="url")


def run(output: Literal["human", "json"]) -> None:
    result = DeploymentResult(
        id="dep_123",
        slug="demo-main",
        status="ready",
        url="https://demo-main.fastapicloud.app",
    )

    style = TaggedStyle(
        tag_width=8,
        theme={
            "tag.title": "black on #A7E3A2",
            "tag": "white on #893AE3",
        },
    )

    with RichToolkit(style=style, mode=output) as toolkit:
        toolkit.print_title("Custom output renderer", tag="demo")
        toolkit.output(result, render_output=render_deployment_output)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", choices=["human", "json"], default="human")
    args = parser.parse_args()

    run(output=args.output)


if __name__ == "__main__":
    main()
