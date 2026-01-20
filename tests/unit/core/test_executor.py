import pytest
from pytest import MonkeyPatch
import shutil

from horus_audit.core.exceptions import ExecutorError
from horus_audit.core.executor import LocalExecutor


@pytest.mark.executor
def test_local_executor_run_argv() -> None:
    executor = LocalExecutor()

    result = executor.run(argv=["echo", "hello"])
    assert result.code == 0
    assert "hello" in result.stdout


@pytest.mark.executor
def test_local_executor_run_text() -> None:
    executor = LocalExecutor()

    result = executor.run_text("echo", "hello")
    assert result.code == 0
    assert "hello" in result.stdout


@pytest.mark.executor
def test_local_executor_command_not_allowed() -> None:
    executor = LocalExecutor(allowed_commands={"echo"})

    with pytest.raises(ExecutorError):
        executor.run(argv=["printf", "hello"])


@pytest.mark.executor
def test_local_executor_command_not_found(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(shutil, "which", lambda self: None)

    executor = LocalExecutor()

    with pytest.raises(ExecutorError):
        executor.run(argv=["echo", "hello"])
