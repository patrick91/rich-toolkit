from __future__ import annotations

import argparse
import time
from typing import Iterator, Literal

from pydantic import BaseModel

from rich_toolkit import RichToolkit
from rich_toolkit.styles import TaggedStyle


OutputMode = Literal["human", "json"]


class DeploymentResult(BaseModel):
    id: str
    slug: str
    status: str
    url: str


class LogEvent(BaseModel):
    type: Literal["log"] = "log"
    step: str
    message: str


class ResultEvent(BaseModel):
    type: Literal["result"] = "result"
    deployment: DeploymentResult


DEPLOYMENT_LOGS = [
    ("create", "Deployment created"),
    ("upload", "Deployment uploaded"),
    ("build", "Build completed"),
]


def make_result() -> DeploymentResult:
    return DeploymentResult(
        id="dep_123",
        slug="demo-main",
        status="ready",
        url="https://demo-main.fastapicloud.app",
    )


def maybe_sleep(no_delay: bool) -> None:
    if not no_delay:
        time.sleep(0.1)


def deployment_events(no_delay: bool) -> Iterator[BaseModel]:
    for step, message in DEPLOYMENT_LOGS:
        maybe_sleep(no_delay)
        yield LogEvent(step=step, message=message)

    yield ResultEvent(deployment=make_result())


def run_human(no_delay: bool) -> None:
    style = TaggedStyle(tag_width=10)

    with RichToolkit(style=style) as toolkit:
        toolkit.print_title("Streaming deployment", tag="demo")
        toolkit.print_line()

        with toolkit.progress("Deploying app", inline_logs=True) as progress:
            for _step, message in DEPLOYMENT_LOGS:
                maybe_sleep(no_delay)
                progress.log(message)

        toolkit.print_line()
        toolkit.output(make_result())


def run(output: OutputMode, no_delay: bool) -> None:
    if output == "json":
        with RichToolkit(mode="json") as toolkit:
            toolkit.output(deployment_events(no_delay=no_delay))
        return

    run_human(no_delay=no_delay)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", choices=["human", "json"], default="human")
    parser.add_argument("--no-delay", action="store_true")
    args = parser.parse_args()

    run(output=args.output, no_delay=args.no_delay)


if __name__ == "__main__":
    main()
