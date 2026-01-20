import pytest

from horus_audit.core.registry import ControlRegistry


@pytest.mark.registry
def test_registry_get() -> None:
    registry = ControlRegistry()

    @registry.register("control")
    def f(**kwargs):
        return "PASSED"

    assert registry.get("control") is f


@pytest.mark.registry
def test_registry_duplicate() -> None:
    registry = ControlRegistry()

    @registry.register("control")
    def f_1(**kwargs):
        return "PASSED"

    with pytest.raises(ValueError):
        @registry.register("control")
        def f_2(**kwargs):
            return "PASSED"
