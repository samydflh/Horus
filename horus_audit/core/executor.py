from dataclasses import dataclass
import subprocess


@dataclass
class ExecutionResult:
    stdout: str
    stderr: str
    code: int


class Executor:
    """
    Execution backend.
    """

    def run(self, cmd: str, timeout: int = 10) -> ExecutionResult:
        raise NotImplementedError


class LocalExecutor(Executor):
    """
    Local subprocess executor.
    """

    def run(self, cmd: str, timeout: int = 10) -> ExecutionResult:
        process = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        return ExecutionResult(
            stdout=process.stdout.rstrip("\n"),
            stderr=process.stderr.rstrip("\n"),
            code=process.returncode
        )
