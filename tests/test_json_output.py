from __future__ import annotations

import json
from dataclasses import dataclass

import pytest
from pydantic import BaseModel

from rich_toolkit import RichToolkit
from rich_toolkit.input import Input
from rich_toolkit.menu import Menu
from rich_toolkit.progress import Progress
from rich_toolkit.styles import MinimalStyle, TaggedStyle


@dataclass
class DataclassDeploymentData:
    id: str
    url: str


class DeploymentData(BaseModel):
    id: str
    url: str


class DeploymentModel(BaseModel):
    id: str = "dep_model"
    url: str = "https://model.fastapicloud.com"


class NotJsonSerializable:
    pass


def test_json_mode_skips_context_spacing_and_human_prints(capsys: pytest.CaptureFixture[str]) -> None:
    app = RichToolkit(style=MinimalStyle(theme={}), mode="json")

    with app:
        app.print_title("Starting deployment")
        app.print("Deploying app...")
        app.print_line()

    captured = capsys.readouterr()

    assert captured.out == ""


def test_json_mode_output_writes_parseable_json_once(capsys: pytest.CaptureFixture[str]) -> None:
    app = RichToolkit(style=MinimalStyle(theme={}), mode="json")

    app.output({"ok": True, "project": "demo"})

    captured = capsys.readouterr()

    assert captured.out == '{"ok": true, "project": "demo"}\n'
    assert json.loads(captured.out) == {"ok": True, "project": "demo"}

    with pytest.raises(RuntimeError, match="output\\(\\) was already called"):
        app.output({"ok": False})


def test_json_mode_output_streams_iterators_as_json_lines(
    capsys: pytest.CaptureFixture[str],
) -> None:
    app = RichToolkit(mode="json")

    def events():
        yield {"type": "log", "message": "Deployment created"}
        yield DeploymentData(id="dep_123", url="https://demo.fastapicloud.com")

    app.output(events())

    captured = capsys.readouterr()
    lines = captured.out.splitlines()

    assert [json.loads(line) for line in lines] == [
        {"type": "log", "message": "Deployment created"},
        {"id": "dep_123", "url": "https://demo.fastapicloud.com"},
    ]

    with pytest.raises(RuntimeError, match="output\\(\\) was already called"):
        app.output({"ok": False})


def test_json_mode_output_keeps_lists_as_one_json_value(
    capsys: pytest.CaptureFixture[str],
) -> None:
    app = RichToolkit(mode="json")

    app.output([{"type": "log"}, {"type": "result"}])

    captured = capsys.readouterr()

    assert captured.out == '[{"type": "log"}, {"type": "result"}]\n'


def test_json_mode_can_be_constructed_without_style(capsys: pytest.CaptureFixture[str]) -> None:
    app = RichToolkit(mode="json")

    app.output({"ok": True})

    captured = capsys.readouterr()

    assert json.loads(captured.out) == {"ok": True}


def test_human_mode_output_uses_explicit_render_output_renderable(
    capsys: pytest.CaptureFixture[str],
) -> None:
    app = RichToolkit(style=MinimalStyle(theme={}))

    app.output(
        {"ok": True, "project": "demo"},
        render_output="Deployment complete: [bold]demo[/bold]",
    )

    captured = capsys.readouterr()

    assert captured.out == "Deployment complete: demo\n"


def test_human_mode_output_uses_explicit_render_output_callable(
    capsys: pytest.CaptureFixture[str],
) -> None:
    app = RichToolkit(style=MinimalStyle(theme={}))

    app.output(
        DeploymentData(id="dep_123", url="https://demo.fastapicloud.com"),
        render_output=lambda deployment: f"Deployment complete: {deployment.id}",
    )

    captured = capsys.readouterr()

    assert captured.out == "Deployment complete: dep_123\n"


def test_human_mode_output_callback_can_print_with_toolkit(
    capsys: pytest.CaptureFixture[str],
) -> None:
    app = RichToolkit(style=TaggedStyle(tag_width=10))

    def render_deployment(deployment: DeploymentData, toolkit: RichToolkit) -> None:
        toolkit.print(deployment.id, tag="deploy")
        toolkit.print(deployment.url, tag="url")

    app.output(
        DeploymentData(id="dep_123", url="https://demo.fastapicloud.com"),
        render_output=render_deployment,
    )

    captured = capsys.readouterr()

    assert " deploy " in captured.out
    assert "dep_123" in captured.out
    assert " url " in captured.out
    assert "https://demo.fastapicloud.com" in captured.out


def test_human_mode_output_renders_pydantic_model_as_name_value_lines_by_default(
    capsys: pytest.CaptureFixture[str],
) -> None:
    app = RichToolkit(style=MinimalStyle(theme={}))

    app.output(DeploymentData(id="dep_123", url="https://demo.fastapicloud.com"))

    captured = capsys.readouterr()

    assert captured.out == "id: dep_123\nurl: https://demo.fastapicloud.com\n"


def test_human_mode_output_renders_dict_as_name_value_lines_by_default(
    capsys: pytest.CaptureFixture[str],
) -> None:
    app = RichToolkit(style=MinimalStyle(theme={}))

    app.output({"id": "dep_123", "url": "https://demo.fastapicloud.com"})

    captured = capsys.readouterr()

    assert captured.out == "id: dep_123\nurl: https://demo.fastapicloud.com\n"


def test_human_mode_output_renders_pydantic_style_model_as_name_value_lines_by_default(
    capsys: pytest.CaptureFixture[str],
) -> None:
    app = RichToolkit(style=MinimalStyle(theme={}))

    app.output(DeploymentModel())

    captured = capsys.readouterr()

    assert captured.out == "id: dep_model\nurl: https://model.fastapicloud.com\n"


def test_human_mode_output_renders_list_of_flat_objects_as_name_value_lines_by_default(
    capsys: pytest.CaptureFixture[str],
) -> None:
    app = RichToolkit(style=MinimalStyle(theme={}))

    app.output(
        [
            {"id": "dep_123", "status": "ready"},
            {"id": "dep_456", "status": "building"},
        ]
    )

    captured = capsys.readouterr()

    assert captured.out == (
        "id: dep_123\n"
        "status: ready\n"
        "\n"
        "id: dep_456\n"
        "status: building\n"
    )


def test_human_mode_output_renders_iterators_item_by_item(
    capsys: pytest.CaptureFixture[str],
) -> None:
    app = RichToolkit(style=MinimalStyle(theme={}))

    app.output(
        iter(
            [
                {"id": "dep_123", "status": "ready"},
                {"id": "dep_456", "status": "building"},
            ]
        )
    )

    captured = capsys.readouterr()

    assert captured.out == (
        "id: dep_123\n"
        "status: ready\n"
        "id: dep_456\n"
        "status: building\n"
    )


def test_print_as_string_still_renders_in_json_mode(
    capsys: pytest.CaptureFixture[str],
) -> None:
    app = RichToolkit(style=MinimalStyle(theme={}), mode="json")

    result = app.print_as_string("Deployment complete")

    captured = capsys.readouterr()

    assert result == "Deployment complete"
    assert captured.out == ""


def test_plain_json_mode_progress_is_quiet(capsys: pytest.CaptureFixture[str]) -> None:
    app = RichToolkit(mode="json")

    with app.progress("Creating deployment") as progress:
        assert isinstance(progress, Progress)
        progress.log("Uploading deployment")
        progress.set_error("Upload failed")

    captured = capsys.readouterr()

    assert captured.out == ""
    assert progress.current_message == "Upload failed"
    assert progress.is_error is True


def test_json_mode_input_raises_without_prompting(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = RichToolkit(mode="json")
    monkeypatch.setattr(Input, "ask", lambda self: "demo")

    with pytest.raises(RuntimeError, match="input\\(\\) is not available in JSON mode"):
        app.input("Project name")


def test_json_mode_ask_raises_without_prompting(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = RichToolkit(mode="json")
    monkeypatch.setattr(Menu, "ask", lambda self: "demo")

    with pytest.raises(RuntimeError, match="ask\\(\\) is not available in JSON mode"):
        app.ask("Project", [{"name": "Demo", "value": "demo"}])


def test_json_mode_confirm_raises_without_prompting(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = RichToolkit(mode="json")
    monkeypatch.setattr(RichToolkit, "ask", lambda self, *args, **kwargs: True)

    with pytest.raises(RuntimeError, match="confirm\\(\\) is not available in JSON mode"):
        app.confirm("Continue?")


def test_json_mode_output_rejects_dataclasses(capsys: pytest.CaptureFixture[str]) -> None:
    app = RichToolkit(mode="json")

    with pytest.raises(
        TypeError,
        match="Object of type DataclassDeploymentData is not JSON serializable",
    ):
        app.output(
            DataclassDeploymentData(
                id="dep_123",
                url="https://demo.fastapicloud.com",
            )
        )

    captured = capsys.readouterr()

    assert captured.out == ""


def test_json_mode_output_serializes_pydantic_style_models(
    capsys: pytest.CaptureFixture[str],
) -> None:
    app = RichToolkit(mode="json")

    app.output(DeploymentModel())

    captured = capsys.readouterr()

    assert json.loads(captured.out) == {
        "id": "dep_model",
        "url": "https://model.fastapicloud.com",
    }


def test_json_mode_output_rejects_unknown_objects(
    capsys: pytest.CaptureFixture[str],
) -> None:
    app = RichToolkit(mode="json")

    with pytest.raises(
        TypeError, match="Object of type NotJsonSerializable is not JSON serializable"
    ):
        app.output(NotJsonSerializable())

    captured = capsys.readouterr()

    assert captured.out == ""


def test_json_mode_output_rejects_non_finite_floats(
    capsys: pytest.CaptureFixture[str],
) -> None:
    app = RichToolkit(mode="json")

    with pytest.raises(ValueError, match="Out of range float values"):
        app.output({"cpu": float("inf")})

    captured = capsys.readouterr()

    assert captured.out == ""

    app.output({"cpu": 1.0})

    captured = capsys.readouterr()

    assert json.loads(captured.out) == {"cpu": 1.0}
