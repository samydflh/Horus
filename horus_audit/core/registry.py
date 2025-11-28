from collections.abc import Callable
from typing import Any

from horus_audit.core.result import ControlResult


ControlFn = Callable[..., ControlResult]


class ControlRegistry:
    """
    Registry of controls.
    """

    def __init__(self) -> None:
        self._controls: dict[str, ControlFn] = {}

    def register(self, name: str) -> Callable[[ControlFn], ControlFn]:
        """
        Decorator to register a control by name.
        """

        def decorator(fn: ControlFn) -> ControlFn:
            if name in self._controls:
                raise ValueError(f"Control registered: {name}")

            self._controls[name] = fn
            return fn

        return decorator

    def get_control(self, name: str) -> ControlFn:
        """
        Retrieve a control by name.
        """

        if name not in self._controls:
            raise KeyError(f"Unknown control: {name}")

        return self._controls[name]

    def list_controls(self) -> list[str]:
        """
        Retrieve all controls.
        """

        return sorted(self._controls.keys())

    def as_jinja_globals(self) -> dict[str, Any]:
        """
        Expose controls as Jinja globals.
        """

        return dict(self._controls)


registry = ControlRegistry()
register_control = registry.register
