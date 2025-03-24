from typing import Any, Callable, Optional


from .element import Element


class Button(Element):
    def __init__(
        self,
        name: str,
        label: str,
        callback: Optional[Callable] = None,
        **metadata: Any,
    ):
        self.name = name
        self.label = label
        self.callback = callback

        super().__init__(**metadata)

    def activate(self) -> Any:
        if self.callback:
            return self.callback()
        return True
