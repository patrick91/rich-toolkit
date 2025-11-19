---
release type: minor
---

Add Pydantic v1/v2 compatibility for Input validators using a Protocol-based approach.

The `Input` component now accepts any object with a `validate_python` method through the new `Validator` protocol, making it compatible with both Pydantic v1 and v2.

**Usage with Pydantic v2:**
```python
from pydantic import TypeAdapter

validator = TypeAdapter(int)
app.input("Enter a number:", validator=validator)
```

**Usage with Pydantic v1:**
```python
from pydantic import parse_obj_as

class V1Validator:
    def __init__(self, type_):
        self.type_ = type_

    def validate_python(self, value):
        return parse_obj_as(self.type_, value)

validator = V1Validator(int)
app.input("Enter a number:", validator=validator)
```

**Changes:**
- Added `Validator` protocol that accepts any object with a `validate_python` method
- Improved error message extraction from Pydantic validation errors
- Added cross-version compatibility tests
- Updated CI to test both Pydantic v1 and v2 across Python 3.8-3.14
