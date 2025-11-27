import pytest
from pytest import MonkeyPatch

from horus_audit.controls.base.services import check_service_enabled
from horus_audit.core.executor import ExecutionResult, LocalExecutor
from horus_audit.core.result import ControlResult


@pytest.mark.services
def test_check_service_enabled_passed(monkeypatch: MonkeyPatch) -> None:
    mock_result = ExecutionResult(
        stdout="enabled",
        stderr="",
        code=0
    )

    mock_executor = LocalExecutor()
    monkeypatch.setattr(mock_executor, "run", lambda cmd: mock_result)

    result = check_service_enabled(
        "ssh",
        executor=mock_executor,
        control_name="test_service_enabled"
    )

    assert isinstance(result, ControlResult)
    assert result.status == "PASSED"
    assert result.name == "test_service_enabled"
    assert "ssh enabled" in result.message


@pytest.mark.services
def test_check_service_enabled_failed(monkeypatch: MonkeyPatch) -> None:
    mock_result = ExecutionResult(
        stdout="disabled",
        stderr="",
        code=0
    )

    mock_executor = LocalExecutor()
    monkeypatch.setattr(mock_executor, "run", lambda cmd: mock_result)

    result = check_service_enabled(
        "ssh",
        executor=mock_executor,
        control_name="test_service_enabled"
    )

    assert isinstance(result, ControlResult)
    assert result.status == "FAILED"
    assert result.name == "test_service_enabled"
    assert "ssh not enabled" in result.message
    assert "disabled" in result.message
