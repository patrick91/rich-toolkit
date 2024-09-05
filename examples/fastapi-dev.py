import uvicorn

from rich_toolkit import App, AppTheme
from rich_toolkit.app_style import TaggedAppStyle
from uvicorn.logging import DefaultFormatter


them = AppTheme(
    style=TaggedAppStyle(tag_width=9),
    theme={
        "tag.title": "black on #A7E3A2",
        "tag": "white on #893AE3",
        "placeholder": "grey85",
        "text": "white",
        "selected": "green",
        "result": "grey85",
        "progress": "on #893AE3",
    },
)


with App(theme=them) as app:
    app.print_title("Starting development server 🌐", tag="FastAPI")

    app.print_line()

    app.print("Searching for package file structure...")

    app.print_line()

    app.print("Found [underline]app[/] package.", tag="app")

    app.print_line()

    app.print("Starting server...")

    app.print_line()

    app.print(
        "Server started at [link=https://localhost:8000]https://localhost:8000[/]",
        tag="server",
    )

    app.print(
        "Documentation at [link=https://localhost:8000/docs]https://localhost:8000/docs[/]"
    )

    app.print_line()

    app.print("Logs:")

    app.print_line()

    class CustomFormatter(DefaultFormatter):
        def formatMessage(self, record):
            return app.print_as_string(record.message, tag=record.levelname)

    log_config = {
        "version": 1,
        "formatters": {
            "default": {
                "()": CustomFormatter,
                "fmt": "%(levelprefix)s %(message)s",
                "use_colors": None,
            },
            "access": {
                "()": CustomFormatter,
                "fmt": "%(levelprefix)s %(client_addr)s - '%(request_line)s' %(status_code)s",
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
            "access": {
                "formatter": "access",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "uvicorn": {"handlers": ["default"], "level": "INFO"},
            "uvicorn.error": {"level": "INFO"},
            "uvicorn.access": {
                "handlers": ["access"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }

    uvicorn.run(
        app="app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_config=log_config,
    )
