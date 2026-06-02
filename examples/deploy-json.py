from __future__ import annotations

import argparse
import time
from typing import Literal

from pydantic import BaseModel

from rich_toolkit import RichToolkit
from rich_toolkit.styles import TaggedStyle


class DeploymentResult(BaseModel):
    id: str
    app_id: str
    slug: str
    status: str
    dashboard_url: str
    url: str


def deploy(output: Literal["human", "json"], skip_wait: bool) -> None:
    style = TaggedStyle(tag_width=10)

    with RichToolkit(style=style, mode=output) as toolkit:
        toolkit.print_title("Starting deployment", tag="FastAPI")
        toolkit.print_line()

        toolkit.print("Deploying app...", tag="deploy")
        toolkit.print_line()

        with toolkit.progress(
            "Creating deployment",
            deployment_id="dep_123",
            app_id="app_456",
        ) as progress:
            time.sleep(0.1)
            progress.log("Deployment created successfully! Deployment slug: demo-main")
            time.sleep(0.1)
            progress.log("Uploading deployment (2.45 MB)...")
            time.sleep(0.1)
            progress.log("Deployment uploaded successfully!")

        if not skip_wait:
            toolkit.print_line()
            toolkit.print("Checking the status of your deployment", tag="cloud")
            toolkit.print_line()

            with toolkit.progress(
                "Waiting for build logs...",
                inline_logs=True,
                deployment_id="dep_123",
            ) as progress:
                for message in [
                    "🔧 Installing dependencies",
                    "🏗️ Running build command",
                    "🚀 Starting application",
                    "🌟 Build complete!",
                ]:
                    time.sleep(0.1)
                    progress.log(message)

            toolkit.print_line()

        result = DeploymentResult(
            id="dep_123",
            app_id="app_456",
            slug="demo-main",
            status="ready",
            dashboard_url="https://fastapicloud.com/apps/demo-main/deployments/dep_123",
            url="https://demo-main.fastapicloud.app",
        )

        toolkit.output(result)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", choices=["human", "json"], default="human")
    parser.add_argument("--no-wait", action="store_true")
    args = parser.parse_args()

    deploy(output=args.output, skip_wait=args.no_wait)


if __name__ == "__main__":
    main()
