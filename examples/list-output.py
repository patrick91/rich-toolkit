from __future__ import annotations

import argparse
from typing import Literal

from pydantic import BaseModel

from rich_toolkit import RichToolkit
from rich_toolkit.styles import TaggedStyle


OutputMode = Literal["human", "json"]


class DeploymentResult(BaseModel):
    id: str
    status: str
    url: str


class LogEvent(BaseModel):
    type: Literal["log"] = "log"
    message: str


class ResultEvent(BaseModel):
    type: Literal["result"] = "result"
    deployment: DeploymentResult


def make_events() -> list[BaseModel]:
    deployment = DeploymentResult(
        id="dep_123",
        status="ready",
        url="https://demo-main.fastapicloud.app",
    )

    return [
        LogEvent(message="Deployment created"),
        LogEvent(message="Deployment uploaded"),
        ResultEvent(deployment=deployment),
    ]


def run(output: OutputMode) -> None:
    style = TaggedStyle(tag_width=8)

    with RichToolkit(style=style, mode=output) as toolkit:
        toolkit.print_title("List output", tag="demo")
        toolkit.output(make_events())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", choices=["human", "json"], default="human")
    args = parser.parse_args()

    run(output=args.output)


if __name__ == "__main__":
    main()
