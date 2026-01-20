from dataclasses import dataclass
import os
import shutil
import subprocess

from horus_audit.core.exceptions import ExecutorError


@dataclass
class ExecutionResult:
    stdout: str
    stderr: str
    code: int


class Executor:
    def run(
        self,
        argv: list[str],
        *,
        timeout: int = 10
    ) -> ExecutionResult:
        raise NotImplementedError


class LocalExecutor(Executor):
    def __init__(
        self,
        *,
        allowed_commands: set[str] | None = None
    ) -> None:
        self._allowed_commands = allowed_commands

    def run(
        self,
        argv: list[str],
        *,
        timeout: int = 10
    ) -> ExecutionResult:
        if not isinstance(argv, list):
            raise ExecutorError("Command must be a list")

        if len(argv) == 0:
            raise ExecutorError("argv is empty")

        if not all(isinstance(arg, str) and arg for arg in argv):
            raise ExecutorError("argv contains empty values")

        executable = os.path.basename(argv[0])

        if self._allowed_commands is not None and executable not in self._allowed_commands:
            raise ExecutorError(f"Command not allowed: {executable}")

        if not os.path.isabs(argv[0]):
            exe_path = shutil.which(argv[0])

            if not exe_path:
                raise ExecutorError(f"Command not found: {argv[0]}")

            argv[0] = exe_path

        try:
            process = subprocess.run(
                argv,
                shell=False,
                capture_output=True,
                text=True,
                timeout=timeout
            )

        except subprocess.TimeoutExpired as exc:
            return ExecutionResult(
                stdout="",
                stderr=str(exc).capitalize().rstrip("\n"),
                code=124
            )

        except Exception as exc:
            raise ExecutorError(f"Execution failed: {exc}") from exc

        return ExecutionResult(
            stdout=(process.stdout or "").rstrip("\n"),
            stderr=(process.stderr or "").rstrip("\n"),
            code=process.returncode
        )

    def run_text(
        self,
        executable: str,
        *args: str,
        timeout: int = 10
    ) -> ExecutionResult:
        argv = [executable, *args]
        return self.run(argv, timeout=timeout)
