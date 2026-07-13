import argparse
import time

from rich_toolkit import RichToolkit


BUILD_LOGS = [
    (
        "Uploading source",
        "upload: Sending 148 files to the remote builder",
    ),
    (
        "Resolving dependencies",
        "builder: $ uv sync --frozen --no-dev "
        "--python-platform x86_64-unknown-linux-gnu",
    ),
    (
        "Installing dependencies",
        "builder: Installed fastapi, pydantic, uvicorn, "
        "rich-toolkit, and 37 transitive dependencies",
    ),
    (
        "Building image",
        "container: exporting image layer " + "a1b2c3d4" * 16,
    ),
    (
        "Starting deployment",
        "runtime: Waiting for health check at "
        "https://example-application.fastapicloud.dev/health",
    ),
    (
        "Deployment ready",
        "ready: Application is accepting requests",
    ),
]


def run_deployment(
    *,
    preserve_logs: bool,
    delay: float,
) -> None:
    toolkit = RichToolkit(
        preserve_progress_logs=preserve_logs,
    )

    with toolkit.progress(
        "Preparing deployment",
        inline_logs=True,
        lines_to_show=3,
    ) as progress:
        for title, log in BUILD_LOGS:
            progress.title = title
            progress.current_message = title
            progress.log(log)
            time.sleep(delay)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=["both", "normal", "preserved"],
        default="both",
    )
    parser.add_argument("--delay", type=float, default=0.15)
    args = parser.parse_args()

    if args.mode in {"both", "normal"}:
        print("Normal inline progress logs (only the last three remain):")
        run_deployment(preserve_logs=False, delay=args.delay)
        print()

    if args.mode in {"both", "preserved"}:
        print("Preserved progress logs (every message remains a logical line):")
        run_deployment(preserve_logs=True, delay=args.delay)
        print()


if __name__ == "__main__":
    main()
