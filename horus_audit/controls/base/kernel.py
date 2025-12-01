from horus_audit.core.executor import Executor
from horus_audit.core.registry import register_control
from horus_audit.core.result import ControlResult


@register_control("check_sysctl_value")
def check_sysctl_value(
    key: str,
    expected_value: str | int,
    *,
    executor: Executor,
    control_name: str
) -> ControlResult:
    """
    Check whether the value of a sysctl parameter match recommendations.

    Returned status:
    - `PASSED` if the sysctl parameter is compliant.
    - `FAILED` if the sysctl parameter do not match recommendations.
    - `SKIPPED` if the sysctl parameter is unreadable.
    """

    result = executor.run(f"sysctl -n {key}")

    if result.code != 0:
        return ControlResult.skipped_(
            control_name,
            f"Cannot read sysctl {key}"
        )

    sysctl_value = result.stdout.strip()

    if str(expected_value) == sysctl_value:
        return ControlResult.passed_(
            control_name,
            f"{key}={sysctl_value}"
        )

    return ControlResult.failed_(
        control_name,
        f"{key}={sysctl_value}, expected {expected_value}"
    )


@register_control("check_module_available")
def check_module_available(
    module: str,
    *,
    executor: Executor,
    control_name: str
) -> ControlResult:
    """
    Check whether a module is not available.

    Returned status:
    - `PASSED` if the module is not available.
    - `FAILED` otherwise.
    """

    result = executor.run(f"modprobe -n {module}")

    if result.code == 0:
        return ControlResult.failed_(
            control_name,
            f"{module} module is available"
        )

    return ControlResult.passed_(
        control_name,
        f"{module} module is not available"
    )


@register_control("check_module_loadable")
def check_module_loadable(
    module: str,
    *,
    executor: Executor,
    control_name: str
) -> ControlResult:
    """
    Check whether a module is unloadable.

    Returned status:
    - `PASSED` if the module is unloadable.
    - `FAILED` otherwise.
    """

    result = executor.run(
        "find /lib/modules/**/kernel/ "
        f"-type f -name '{module}*'"
    )

    if result.stdout:
        return ControlResult.failed_(
            control_name,
            f"{module} module is loadable"
        )

    return ControlResult.passed_(
        control_name,
        f"{module} module is unloadable"
    )
