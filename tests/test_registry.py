import pytest

from horus_audit.core.registry import ControlRegistry
from horus_audit.core.result import ControlResult


@pytest.mark.registry
def test_registry_initialization() -> None:
    test_registry = ControlRegistry()

    assert isinstance(test_registry._controls, dict)
    assert len(test_registry._controls) == 0


@pytest.mark.registry
def test_register_control() -> None:
    test_registry = ControlRegistry()

    def control(control_name: str) -> ControlResult:
        return ControlResult.passed_(control_name, "test message")

    decorator = test_registry.register("test_control")
    registered_control = decorator(control)

    assert registered_control is control
    assert "test_control" in test_registry._controls
    assert test_registry._controls["test_control"] is control


@pytest.mark.registry
def test_register_control_duplicates() -> None:
    test_registry = ControlRegistry()

    def control_1(control_name: str) -> ControlResult:
        return ControlResult.passed_(control_name, "test message 1")

    def control_2(control_name: str) -> ControlResult:
        return ControlResult.passed_(control_name, "test message 2")

    test_registry.register("test_control")(control_1)

    with pytest.raises(ValueError, match="Control registered: test_control"):
        test_registry.register("test_control")(control_2)


@pytest.mark.registry
def test_get_control() -> None:
    test_registry = ControlRegistry()

    def control(control_name: str) -> ControlResult:
        return ControlResult.passed_(control_name, "test message")

    test_registry.register("test_control")(control)

    retrieved_control = test_registry.get_control("test_control")
    assert retrieved_control is control


@pytest.mark.registry
def test_get_control_unknown() -> None:
    test_registry = ControlRegistry()

    with pytest.raises(KeyError, match="Unknown control: unknown_control"):
        test_registry.get_control("unknown_control")


@pytest.mark.registry
def test_list_controls() -> None:
    test_registry = ControlRegistry()

    def control_1(control_name: str) -> ControlResult:
        return ControlResult.passed_(control_name, "test message 1")

    def control_2(control_name: str) -> ControlResult:
        return ControlResult.passed_(control_name, "test message 2")

    def control_3(control_name: str) -> ControlResult:
        return ControlResult.passed_(control_name, "test message 3")

    test_registry.register("gamma_control")(control_1)
    test_registry.register("alpha_control")(control_2)
    test_registry.register("theta_control")(control_3)

    controls = test_registry.list_controls()
    assert controls == ["alpha_control", "gamma_control", "theta_control"]


@pytest.mark.registry
def test_list_controls_empty() -> None:
    test_registry = ControlRegistry()

    controls = test_registry.list_controls()
    assert len(controls) == 0


@pytest.mark.registry
def test_as_jinja_globals() -> None:
    test_registry = ControlRegistry()

    def control_1(control_name: str) -> ControlResult:
        return ControlResult.passed_(control_name, "test message 1")

    def control_2(control_name: str) -> ControlResult:
        return ControlResult.passed_(control_name, "test message 2")

    test_registry.register("control_1")(control_1)
    test_registry.register("control_2")(control_2)

    globals_dict = test_registry.as_jinja_globals()

    assert "control_1" in globals_dict
    assert "control_2" in globals_dict
    assert globals_dict["control_1"] is control_1
    assert globals_dict["control_2"] is control_2
