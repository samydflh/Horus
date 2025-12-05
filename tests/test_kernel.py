import pytest
from pytest import MonkeyPatch

from horus_audit.controls.base import (
    check_module_available,
    check_sysctl_value
)
from horus_audit.core.executor import ExecutionResult, LocalExecutor


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

    assert result.status == "PASSED"
    assert result.name == "test_sysctl"
    assert result.message == "net.ipv4.ip_forward=1"


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

    assert result.status == "FAILED"
    assert result.name == "test_sysctl"
    assert result.message == "net.ipv4.ip_forward=1, expected 0"


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

    assert result.status == "SKIPPED"
    assert result.name == "test_sysctl"
    assert result.message == "Cannot read sysctl net.invalid.key"


@pytest.mark.kernel
def test_check_module_available_passed(monkeypatch: MonkeyPatch) -> None:
    mock_executor = LocalExecutor()

    monkeypatch.setattr(
        "horus_audit.controls.base.kernel._check_module_exists",
        lambda module, executor: False
    )

    result = check_module_available(
        "cramfs",
        executor=mock_executor,
        control_name="test_module_available"
    )

    assert result.status == "PASSED"
    assert result.name == "test_module_available"
    assert result.message == "cramfs module does not exist"


@pytest.mark.kernel
def test_check_module_available_failed(monkeypatch: MonkeyPatch) -> None:
    mock_executor = LocalExecutor()

    monkeypatch.setattr(
        "horus_audit.controls.base.kernel._check_module_exists",
        lambda module, executor: True
    )
    monkeypatch.setattr(
        "horus_audit.controls.base.kernel._check_module_loaded",
        lambda module, executor: False
    )
    monkeypatch.setattr(
        "horus_audit.controls.base.kernel._check_module_disabled",
        lambda module, executor: False
    )

    result = check_module_available(
        "cramfs",
        executor=mock_executor,
        control_name="test_module_available"
    )

    assert result.status == "FAILED"
    assert result.name == "test_module_available"
    assert result.message == "cramfs module exists, not disabled"
