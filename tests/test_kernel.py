import pytest
from pytest import MonkeyPatch

from horus_audit.controls.base import check_sysctl_value
from horus_audit.core.executor import ExecutionResult, LocalExecutor
from horus_audit.core.result import ControlResult


@pytest.mark.kernel
def test_check_sysctl_value_passed(monkeypatch: MonkeyPatch) -> None:
    mock_result = ExecutionResult(
        stdout="1",
        stderr="",
        code=0
    )

    mock_executor = LocalExecutor()
    monkeypatch.setattr(mock_executor, "run", lambda cmd: mock_result)

    result = check_sysctl_value(
        "net.ipv4.ip_forward",
        1,
        executor=mock_executor,
        control_name="test_sysctl"
    )

    assert isinstance(result, ControlResult)
    assert result.status == "PASSED"
    assert result.name == "test_sysctl"
    assert "net.ipv4.ip_forward=1" in result.message


@pytest.mark.kernel
def test_check_sysctl_value_failed(monkeypatch: MonkeyPatch) -> None:
    mock_result = ExecutionResult(
        stdout="1",
        stderr="",
        code=0
    )

    mock_executor = LocalExecutor()
    monkeypatch.setattr(mock_executor, "run", lambda cmd: mock_result)

    result = check_sysctl_value(
        "net.ipv4.ip_forward",
        0,
        executor=mock_executor,
        control_name="test_sysctl"
    )

    assert isinstance(result, ControlResult)
    assert result.status == "FAILED"
    assert result.name == "test_sysctl"
    assert "net.ipv4.ip_forward=1, expected 0" in result.message


@pytest.mark.kernel
def test_check_sysctl_value_skipped(monkeypatch: MonkeyPatch) -> None:
    mock_result = ExecutionResult(
        stdout="",
        stderr="sysctl: cannot stat /proc/sys/net/invalid/key",
        code=1
    )

    mock_executor = LocalExecutor()
    monkeypatch.setattr(mock_executor, "run", lambda cmd: mock_result)

    result = check_sysctl_value(
        "net.invalid.key",
        1,
        executor=mock_executor,
        control_name="test_sysctl"
    )

    assert isinstance(result, ControlResult)
    assert result.status == "SKIPPED"
    assert result.name == "test_sysctl"
    assert "Cannot read sysctl net.invalid.key" in result.message
