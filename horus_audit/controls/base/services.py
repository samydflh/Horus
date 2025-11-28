from horus_audit.core.executor import Executor
from horus_audit.core.registry import register_control
from horus_audit.core.result import ControlResult


@register_control("check_service_enabled")
def check_service_enabled(
    service: str,
    *,
    executor: Executor,
    control_name: str
) -> ControlResult:
    """
    Check whether a service is enabled.

    Returned status:
    - `PASSED` if the service is enabled.
    - `FAILED` otherwise.
    """

    result = executor.run(f"systemctl is-enabled {service}")

    if result.code == 0 and result.stdout.strip() == "enabled":
        return ControlResult.passed_(control_name, f"{service} enabled")

    return ControlResult.failed_(
        control_name,
        f"{service} not enabled ({result.stdout or result.stderr})"
    )
