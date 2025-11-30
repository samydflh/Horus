import os

from horus_audit.core.executor import Executor
from horus_audit.core.registry import register_control
from horus_audit.core.result import ControlResult


@register_control("check_partition")
def check_partition(
    mount: str,
    expected_fstype: tuple[str, ...],
    expected_options: tuple[str, ...],
    *,
    executor: Executor,
    control_name: str
) -> ControlResult:
    """
    Check whether a separate partition exists.

    Returned status:
    - `PASSED` if the partition is correctly mounted.
    - `FAILED` if the partition does not exist.
    - `WARNING` if the partition setting does not match recommendations.
    """

    result = executor.run(f"findmnt -n -o FSTYPE,OPTIONS {mount}")

    if result.code != 0 or not result.stdout.strip():
        return ControlResult.failed_(
            control_name,
            f"Cannot find {mount} partition"
        )

    fstype, options = result.stdout.strip().split()

    if fstype not in expected_fstype:
        return ControlResult.warning_(
            control_name,
            f"{mount} has {fstype} filesystem, expected {', '.join(expected_fstype)}"
        )

    unset_options = [
        option for option in expected_options
        if option not in set(options.split(","))
    ]

    if unset_options:
        return ControlResult.warning_(
            control_name,
            f"{mount} does not include options {', '.join(unset_options)}"
        )

    return ControlResult.passed_(
        control_name,
        f"{mount} is a separate partition"
    )


@register_control("check_file_exists")
def check_file_exists(
    path: str,
    *,
    control_name: str
) -> ControlResult:
    """
    Check whether a file exists.

    Returned status:
    - `PASSED` if the file exists.
    - `FAILED` otherwise.
    """

    if os.path.exists(path):
        return ControlResult.passed_(
            control_name,
            f"{path} exists"
        )

    return ControlResult.failed_(
        control_name,
        f"{path} does not exist"
    )


@register_control("check_file_permissions")
def check_file_permissions(
    path: str,
    expected_mode: str,
    *,
    control_name: str
) -> ControlResult:
    """
    Check whether a file permissions match recommendations.

    Returned status:
    - `PASSED` if the file permissions are compliant.
    - `FAILED` if the file permissions do not match recommendations.
    - `WARNING` if the file does not exist.
    - `SKIPPED` if the file cannot be read.
    """

    try:
        st = os.stat(path)
        mode = oct(st.st_mode)[-3:]

        if (int(mode, 8) & ~int(expected_mode, 8)) == 0:
            return ControlResult.passed_(
                control_name,
                f"{path} permissions are compliant: {mode}"
            )

        return ControlResult.failed_(
            control_name,
            f"{path} has permissions {mode}, expected {expected_mode}"
        )

    except FileNotFoundError:
        return ControlResult.warning_(
            control_name,
            f"{path} not found"
        )

    except PermissionError:
        return ControlResult.skipped_(
            control_name,
            f"No permission to access {path}"
        )
