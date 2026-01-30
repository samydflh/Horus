from horus_audit.core.executor import Executor
from horus_audit.core.registry import register_control
from horus_audit.core.result import ControlResult


@register_control("filesystem.module_disabled")
def check_filesystem_module_disabled(
    *,
    rule_id: str,
    control: str,
    params: dict,
    executor: Executor
) -> ControlResult:
    """
    Check whether a filesystem module is properly disabled.
    """

    # Kernel module
    module_param = params.get("module")

    if not isinstance(module_param, str) or not module_param.strip():
        return ControlResult.error_(
            rule_id=rule_id,
            control=control,
            message="params.module is empty"
        )

    module = module_param.strip().lower()

    # Check whether the module exists on disk
    find_cmd = executor.run(
        ["find", "/lib/modules/", "-type", "f", "-name", f"{module}*.ko*"]
    )

    exists = bool(find_cmd.stdout.strip())

    if not exists:
        return ControlResult.passed_(
            rule_id=rule_id,
            control=control,
            message=f"Kernel module {module} does not exist"
        )

    # Check whether the module is loaded
    lsmod_cmd = executor.run(["lsmod"])

    if lsmod_cmd.code == 0:
        for line in lsmod_cmd.stdout.splitlines():
            if line.startswith(module + " "):
                return ControlResult.failed_(
                    rule_id=rule_id,
                    control=control,
                    message=f"Kernel module {module} is loaded"
                )

    # Check whether modprobe rules are configured
    grep_cmd = executor.run(["grep", "-RHi", "", "/etc/modprobe.d"])

    install_rule = False
    blacklist_rule = False

    if grep_cmd.code == 0:
        for line in grep_cmd.stdout.splitlines():
            line = line.lower()

            if f"install {module}" in line and (
                "/bin/true" in line or "/bin/false" in line
            ):
                install_rule = True
            if f"blacklist {module}" in line:
                blacklist_rule = True

    if not install_rule or not blacklist_rule:
        return ControlResult.failed_(
            rule_id=rule_id,
            control=control,
            message=f"Kernel module {module} is not disabled"
        )

    return ControlResult.passed_(
        rule_id=rule_id,
        control=control,
        message=f"Kernel module {module} is disabled"
    )


@register_control("filesystem.partition")
def check_filesystem_partition(
    *,
    rule_id: str,
    control: str,
    params: dict,
    executor: Executor
) -> ControlResult:
    """
    Check whether a filesystem path is mounted as a separate partition.
    """

    # Partition
    partition_param = params.get("partition")

    if not isinstance(partition_param, str) or not partition_param.strip():
        return ControlResult.error_(
            rule_id=rule_id,
            control=control,
            message="params.partition is empty"
        )

    partition = partition_param.strip().lower()

    # Filesystem type
    fstype_param = params.get("fstype")

    if not isinstance(fstype_param, list) or not fstype_param:
        return ControlResult.error_(
            rule_id=rule_id,
            control=control,
            message="params.fstype is empty"
        )

    required_fstype = set(fstype_param)

    # Options
    options_param = params.get("options")

    if not isinstance(options_param, list) or not options_param:
        return ControlResult.error_(
            rule_id=rule_id,
            control=control,
            message="params.options is empty"
        )

    required_options = set(options_param)

    # List mounted partitions
    findmnt_cmd = executor.run(
        ["findmnt", "-kno", "TARGET,FSTYPE,OPTIONS", "--target", partition]
    )

    if findmnt_cmd.code != 0 or not findmnt_cmd.stdout.strip():
        return ControlResult.skipped_(
            rule_id=rule_id,
            control=control,
            message=f"Unable to determine mount information for {partition}"
        )

    _, fstype, options = findmnt_cmd.stdout.strip().split(None, 2)

    if fstype not in required_fstype:
        return ControlResult.failed_(
            rule_id=rule_id,
            control=control,
            message=f"{partition} is mounted with an unexpected filesystem type"
        )

    if not required_options.issubset(set(options.split(","))):
        return ControlResult.failed_(
            rule_id=rule_id,
            control=control,
            message=f"{partition} is mounted with unexpected options"
        )

    return ControlResult.passed_(
        rule_id=rule_id,
        control=control,
        message=f"{partition} is properly configured"
    )
