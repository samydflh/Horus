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

    if not _check_module_exists(module, executor):
        return ControlResult.passed_(
            control_name,
            f"{module} module does not exist"
        )

    if _check_module_loaded(module, executor):
        return ControlResult.failed_(
            control_name,
            f"{module} module is loaded"
        )

    if not _check_module_disabled(module, executor):
        return ControlResult.failed_(
            control_name,
            f"{module} module exists, not disabled"
        )

    return ControlResult.passed_(
        control_name,
        f"{module} module exists, not loaded, disabled"
    )


def _check_module_exists(module: str, executor: Executor) -> bool:
    """
    Check whether the module exists.
    """

    result = executor.run(
        "find /lib/modules/**/kernel/ "
        f"-type f -name '{module}*'"
    )

    return bool(result.stdout.strip())


def _check_module_loaded(module: str, executor: Executor) -> bool:
    """
    Check whether the module is loaded.
    """

    result = executor.run("lsmod")

    if result.code != 0:
        return False

    for line in result.stdout.splitlines():
        if line.startswith(module + " "):
            return True

    return False


def _check_module_disabled(module: str, executor: Executor) -> bool:
    """
    Check whether the module is disabled.
    """

    result = executor.run("grep -RHi '' /etc/modprobe.d/ 2>/dev/null")

    if result.code != 0:
        return False

    disabled = False

    for line in result.stdout.splitlines():
        line = line.lower()

        if f"blacklist {module}" in line:
            disabled = True

        if f"install {module}" in line and ("/bin/true" in line or "/bin/false" in line):
            disabled = True

    return disabled
