import pytest
from pytest import MonkeyPatch

from horus_audit.controls.base import (
    check_service_active,
    check_service_enabled
)
from horus_audit.core.executor import ExecutionResult, LocalExecutor


@pytest.mark.services
@pytest.mark.parametrize(
    "stdout",
    [
        "enabled",
        "enabled-runtime",
        "alias"
    ]
)
def test_check_service_enabled_passed(
    monkeypatch: MonkeyPatch,
    stdout: str
) -> None:
    mock_result = ExecutionResult(
        stdout=stdout,
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

    assert result.status == "PASSED"
    assert result.name == "test_service_enabled"
    assert result.message == "ssh enabled"


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

    assert result.status == "FAILED"
    assert result.name == "test_service_enabled"
    assert result.message == "ssh not enabled"


@pytest.mark.services
@pytest.mark.parametrize(
    "stdout",
    [
        "disabled",
        "masked",
        "static",
        "indirect"
    ]
)
def test_check_service_disabled_passed(
    monkeypatch: MonkeyPatch,
    stdout: str
) -> None:
    mock_result = ExecutionResult(
        stdout=stdout,
        stderr="",
        code=0
    )

    mock_executor = LocalExecutor()
    monkeypatch.setattr(mock_executor, "run", lambda cmd: mock_result)

    result = check_service_enabled(
        "ssh",
        enabled=False,
        executor=mock_executor,
        control_name="test_service_disabled"
    )

    assert result.status == "PASSED"
    assert result.name == "test_service_disabled"
    assert result.message == "ssh disabled"


@pytest.mark.services
def test_check_service_disabled_failed(monkeypatch: MonkeyPatch) -> None:
    mock_result = ExecutionResult(
        stdout="enabled",
        stderr="",
        code=0
    )

    mock_executor = LocalExecutor()
    monkeypatch.setattr(mock_executor, "run", lambda cmd: mock_result)

    result = check_service_enabled(
        "ssh",
        enabled=False,
        executor=mock_executor,
        control_name="test_service_disabled"
    )

    assert result.status == "FAILED"
    assert result.name == "test_service_disabled"
    assert result.message == "ssh not disabled"


@pytest.mark.services
@pytest.mark.parametrize(
    "stdout",
    [
        "active",
        "active (running)",
        "active (exited)",
        "active (listening)"
    ]
)
def test_check_service_active_passed(
    monkeypatch: MonkeyPatch,
    stdout: str
) -> None:
    mock_result = ExecutionResult(
        stdout=stdout,
        stderr="",
        code=0
    )

    mock_executor = LocalExecutor()
    monkeypatch.setattr(mock_executor, "run", lambda cmd: mock_result)

    result = check_service_active(
        "ssh",
        executor=mock_executor,
        control_name="test_service_active"
    )

    assert result.status == "PASSED"
    assert result.name == "test_service_active"
    assert result.message == "ssh active"


@pytest.mark.services
def test_check_service_active_failed(monkeypatch: MonkeyPatch) -> None:
    mock_result = ExecutionResult(
        stdout="inactive",
        stderr="",
        code=3
    )

    mock_executor = LocalExecutor()
    monkeypatch.setattr(mock_executor, "run", lambda cmd: mock_result)

    result = check_service_active(
        "ssh",
        executor=mock_executor,
        control_name="test_service_active"
    )

    assert result.status == "FAILED"
    assert result.name == "test_service_active"
    assert result.message == "ssh not active"


@pytest.mark.services
@pytest.mark.parametrize(
    "stdout",
    [
        "inactive",
        "inactive (dead)",
        "failed"
    ]
)
def test_check_service_inactive_passed(
    monkeypatch: MonkeyPatch,
    stdout: str
) -> None:
    mock_result = ExecutionResult(
        stdout=stdout,
        stderr="",
        code=3
    )

    mock_executor = LocalExecutor()
    monkeypatch.setattr(mock_executor, "run", lambda cmd: mock_result)

    result = check_service_active(
        "ssh",
        active=False,
        executor=mock_executor,
        control_name="test_service_inactive"
    )

    assert result.status == "PASSED"
    assert result.name == "test_service_inactive"
    assert result.message == "ssh not active"


@pytest.mark.services
def test_check_service_inactive_failed(monkeypatch: MonkeyPatch) -> None:
    mock_result = ExecutionResult(
        stdout="active",
        stderr="",
        code=0
    )

    mock_executor = LocalExecutor()
    monkeypatch.setattr(mock_executor, "run", lambda cmd: mock_result)

    result = check_service_active(
        "ssh",
        active=False,
        executor=mock_executor,
        control_name="test_service_inactive"
    )

    assert result.status == "FAILED"
    assert result.name == "test_service_inactive"
    assert result.message == "ssh active"
