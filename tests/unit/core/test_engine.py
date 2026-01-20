import pytest

from horus_audit.core.engine import run_policy
from horus_audit.core.rule import Policy, Rule


class Executor:
    def run(self, argv, timeout: int = 10):
        class ExecutionResult:
            stdout = ""
            stderr = ""
            code = 0

        return ExecutionResult()


@pytest.mark.engine
def test_engine_unknown_control_error() -> None:
    policy = Policy(
        category="Unit tests",
        rules=[
            Rule(
                rule_id="R1",
                control="Test control",
                params={}
            )
        ]
    )

    results = run_policy(policy, executor=Executor())
    assert results[0].status == "ERROR"
