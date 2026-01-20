from collections.abc import Callable

from horus_audit.core.result import ControlResult


ControlFunction = Callable[..., ControlResult]


class ControlRegistry:
    def __init__(self) -> None:
        self._controls = {}

    def register(self, name: str) -> Callable[[ControlFunction], ControlFunction]:
        def decorator(f: ControlFunction) -> ControlFunction:
            if name in self._controls:
                raise ValueError(f"Control registered: {name}")

            self._controls[name] = f
            return f

        return decorator

    def get(self, name: str) -> ControlFunction:
        if name not in self._controls:
            raise KeyError(f"Unknown control: {name}")

        return self._controls[name]

    def has(self, name: str) -> bool:
        return name in self._controls

    def list_controls(self) -> list[str]:
        return sorted(self._controls.keys())


registry = ControlRegistry()
register_control = registry.register
