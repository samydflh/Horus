from horus_audit.core.executor import Executor
from horus_audit.core.registry import register_control
from horus_audit.core.result import ControlResult


@register_control("check_service_enabled")
def check_service_enabled(
    service: str,
    enabled: bool = True,
    *,
    executor: Executor,
    control_name: str
) -> ControlResult:
    """
    Check whether a service is enabled, based on the `enabled` requirement.

    Returned status:
    - If `enabled` is True:
        - `PASSED` if the service is enabled.
        - `FAILED` if the service is disabled.
    - If `enabled` is False:
        - `PASSED` if the service is disabled.
        - `FAILED` if the service is enabled.
    """

    result = executor.run(f"systemctl is-enabled {service} 2>/dev/null | grep 'enabled'")

    if enabled:
        if result.code == 0 and result.stdout.strip():
            return ControlResult.passed_(
                control_name,
                f"{service} enabled"
            )

        return ControlResult.failed_(
            control_name,
            f"{service} disabled"
        )
    else:
        if not result.stdout.strip():
            return ControlResult.passed_(
                control_name,
                f"{service} disabled"
            )

        return ControlResult.failed_(
            control_name,
            f"{service} enabled"
        )


@register_control("check_service_active")
def check_service_active(
    service: str,
    active: bool = True,
    *,
    executor: Executor,
    control_name: str
) -> ControlResult:
    """
    Check whether a service is active, based on the `active` requirement.

    Returned status:
    - If `active` is True:
        - `PASSED` if the service is active.
        - `FAILED` otherwise.
    - If `active` is False:
        - `PASSED` if the service is not active.
        - `FAILED` otherwise.
    """

    result = executor.run(f"systemctl is-active {service} 2>/dev/null | grep '^active'")

    if active:
        if result.code == 0 and result.stdout.strip():
            return ControlResult.passed_(
                control_name,
                f"{service} active"
            )

        return ControlResult.failed_(
            control_name,
            f"{service} inactive"
        )
    else:
        if not result.stdout.strip():
            return ControlResult.passed_(
                control_name,
                f"{service} inactive"
            )

        return ControlResult.failed_(
            control_name,
            f"{service} active"
        )
