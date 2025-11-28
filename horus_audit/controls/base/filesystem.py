import os

from horus_audit.core.registry import register_control
from horus_audit.core.result import ControlResult


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
        return ControlResult.passed_(control_name, f"{path} exists")

    return ControlResult.failed_(control_name, f"{path} does not exist")


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

        if mode == expected_mode:
            return ControlResult.passed_(control_name, f"{path} permissions are compliant: {mode}")

        return ControlResult.failed_(
            control_name,
            f"{path} has permissions {mode}, expected {expected_mode}"
        )

    except FileNotFoundError:
        return ControlResult.warning_(control_name, f"{path} not found")

    except PermissionError:
        return ControlResult.skipped_(control_name, f"No permission to access {path}")
