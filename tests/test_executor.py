import subprocess
from unittest.mock import Mock

import pytest
from pytest import MonkeyPatch

from horus_audit.core.executor import ExecutionResult, Executor, LocalExecutor


@pytest.mark.executor
def test_execution_result() -> None:
    result = ExecutionResult(
        stdout="output",
        stderr="error",
        code=0
    )

    assert result.stdout == "output"
    assert result.stderr == "error"
    assert result.code == 0


@pytest.mark.executor
def test_executor_backend() -> None:
    executor = Executor()

    with pytest.raises(NotImplementedError):
        executor.run("test command")


@pytest.mark.executor
def test_local_executor_success(monkeypatch: MonkeyPatch) -> None:
    mock_process = Mock()
    mock_process.stdout = "test output\n"
    mock_process.stderr = ""
    mock_process.returncode = 0

    mock_run = Mock(return_value=mock_process)
    monkeypatch.setattr("subprocess.run", mock_run)

    executor = LocalExecutor()
    result = executor.run("echo test")

    mock_run.assert_called_once_with(
        "echo test",
        shell=True,
        capture_output=True,
        text=True,
        timeout=10
    )

    assert result.stdout == "test output"
    assert result.stderr == ""
    assert result.code == 0


@pytest.mark.executor
def test_local_executor_failure(monkeypatch: MonkeyPatch) -> None:
    mock_process = Mock()
    mock_process.stdout = ""
    mock_process.stderr = "command not found\n"
    mock_process.returncode = 127

    mock_run = Mock(return_value=mock_process)
    monkeypatch.setattr("subprocess.run", mock_run)

    executor = LocalExecutor()
    result = executor.run("non_existent_command")

    assert result.stdout == ""
    assert result.stderr == "command not found"
    assert result.code == 127


@pytest.mark.executor
def test_local_executor_timeout(monkeypatch: MonkeyPatch) -> None:
    mock_run = Mock(side_effect=subprocess.TimeoutExpired("sleep 10", 5))
    monkeypatch.setattr("subprocess.run", mock_run)

    executor = LocalExecutor()

    with pytest.raises(subprocess.TimeoutExpired):
        executor.run("sleep 10", timeout=5)
