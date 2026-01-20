from dataclasses import dataclass
from typing import Any

from horus_audit.core.executor import Executor, LocalExecutor
from horus_audit.core.registry import registry
from horus_audit.core.result import ControlResult
from horus_audit.core.rule import Policy, Rule


@dataclass
class EngineContext:
    executor: Executor
    os_info: Any | None = None


def run_policy(
    policy: Policy,
    *,
    executor: Executor | None = None,
    os_info: Any | None = None
) -> list[ControlResult]:
    """
    Execute a validated policy.

    Args:
        policy (Policy): Validated policy.
        executor (Executor | None, optional): Execution backend. Defaults to None.
        os_info (Any | None, optional): OS information. Defaults to None.

    Returns:
        list[ControlResult]: Control results.
    """

    backend = executor or LocalExecutor()
    context = EngineContext(executor=backend, os_info=os_info)

    results = []

    for rule in policy.rules:
        results.append(_execute_rule(rule, context))

    return results


def _execute_rule(rule: Rule, context: EngineContext) -> ControlResult:
    if not registry.has(rule.control):
        return ControlResult.error_(
            rule_id=rule.rule_id,
            control=rule.control,
            message=f"Unknown control: {rule.control}"
        )

    f = registry.get(rule.control)

    try:
        return f(
            rule_id=rule.rule_id,
            control=rule.control,
            params=rule.params,
            executor=context.executor,
            os_info=context.os_info
        )

    except Exception as exc:
        return ControlResult.error_(
            rule_id=rule.rule_id,
            control=rule.control,
            message=str(exc).capitalize()
        )
