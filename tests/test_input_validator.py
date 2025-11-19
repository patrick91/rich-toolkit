from typing import Any

from rich_toolkit.input import Input

try:
    from pydantic import TypeAdapter

    PYDANTIC_V2 = True

    # Use TypeAdapter for Pydantic v2
    int_validator = TypeAdapter(int)

except ImportError:
    from pydantic import parse_obj_as

    PYDANTIC_V2 = False

    # Create a wrapper for Pydantic v1
    class V1IntValidator:
        def __init__(self, type_):
            self.type_ = type_

        def validate_python(self, value: Any) -> Any:
            return parse_obj_as(self.type_, value)

    int_validator = V1IntValidator(int)


def test_validator_with_valid_input():
    """Test that validation works with valid input (Pydantic v1 and v2 compatible)."""
    input_field = Input(validator=int_validator)  # type: ignore
    input_field.text = "123"

    input_field.on_validate()

    assert input_field.valid is True
    assert input_field._validation_message is None


def test_validator_with_invalid_input():
    """Test that validation fails with invalid input (Pydantic v1 and v2 compatible)."""
    input_field = Input(validator=int_validator)  # type: ignore
    input_field.text = "not a number"

    input_field.on_validate()

    assert input_field.valid is False
    assert input_field._validation_message is not None
