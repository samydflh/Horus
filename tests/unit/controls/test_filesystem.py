import pytest

from horus_audit.controls import (
    check_filesystem_module_disabled,
    check_filesystem_partition
)
from horus_audit.core.executor import ExecutionResult, Executor


class MockExecutor(Executor):
    def __init__(self, mock_function):
        self._mock_function = mock_function

    def run(self, argv, *, timeout=10):
        return self._mock_function(argv, timeout=timeout)


@pytest.mark.filesystem
def test_module_disabled() -> None:
    def mock_run(argv, **kwargs):
        return ExecutionResult(
            stdout="""/etc/modprobe.d/disable.conf:install cramfs /bin/true
/etc/modprobe.d/blacklist.conf:blacklist cramfs""",
            stderr="",
            code=0
        )

    result = check_filesystem_module_disabled(
        rule_id="filesystem.module_disabled",
        control="Ensure cramfs is properly disabled",
        params={"module": "cramfs"},
        executor=MockExecutor(mock_run)
    )

    assert result.status == "PASSED"
    assert result.message == "Kernel module cramfs is disabled"


@pytest.mark.filesystem
def test_module_disabled_not_exists() -> None:
    result = check_filesystem_module_disabled(
        rule_id="filesystem.module_disabled",
        control="Ensure cramfs is properly disabled",
        params={"module": "cramfs"},
        executor=MockExecutor(
            lambda argv, **kwargs: ExecutionResult(
                stdout="",
                stderr="",
                code=0
            )
        )
    )

    assert result.status == "PASSED"
    assert result.message == "Kernel module cramfs does not exist"


@pytest.mark.filesystem
def test_module_disabled_loaded() -> None:
    def mock_run(argv, **kwargs):
        return ExecutionResult(stdout="/lib/modules/cramfs.ko", stderr="", code=0)

    result = check_filesystem_module_disabled(
        rule_id="filesystem.module_disabled",
        control="Ensure cramfs is properly disabled",
        params={"module": "cramfs"},
        executor=MockExecutor(mock_run)
    )

    assert result.status == "FAILED"
    assert result.message == "Kernel module cramfs is not disabled"


@pytest.mark.filesystem
def test_module_disabled_only_blacklist() -> None:
    def mock_run(argv, **kwargs):
        return ExecutionResult(
            stdout="/etc/modprobe.d/blacklist.conf:blacklist cramfs",
            stderr="",
            code=0
        )

    result = check_filesystem_module_disabled(
        rule_id="filesystem.module_disabled",
        control="Ensure cramfs is properly disabled",
        params={"module": "cramfs"},
        executor=MockExecutor(mock_run)
    )

    assert result.status == "FAILED"
    assert result.message == "Kernel module cramfs is not disabled"


@pytest.mark.filesystem
def test_module_disabled_only_install() -> None:
    def mock_run(argv, **kwargs):
        return ExecutionResult(
            stdout="/etc/modprobe.d/disable.conf:install cramfs /bin/true",
            stderr="",
            code=0
        )

    result = check_filesystem_module_disabled(
        rule_id="filesystem.module_disabled",
        control="Ensure cramfs is properly disabled",
        params={"module": "cramfs"},
        executor=MockExecutor(mock_run)
    )

    assert result.status == "FAILED"
    assert result.message == "Kernel module cramfs is not disabled"


@pytest.mark.filesystem
def test_module_disabled_empty_param() -> None:
    result = check_filesystem_module_disabled(
        rule_id="filesystem.module_disabled",
        control="Ensure cramfs is properly disabled",
        params={"module": ""},
        executor=MockExecutor(lambda argv, **kwargs: ExecutionResult(stdout="", stderr="", code=0))
    )

    assert result.status == "ERROR"
    assert result.message == "params.module is empty"


@pytest.mark.filesystem
def test_partition_configured() -> None:
    result = check_filesystem_partition(
        rule_id="filesystem.partition",
        control="Ensure /tmp is a separate partition",
        params={
            "partition": "/tmp",
            "fstype": ["ext4", "xfs"],
            "options": ["nodev", "nosuid", "noexec"]
        },
        executor=MockExecutor(
            lambda argv, **kwargs: ExecutionResult(
                stdout="/tmp ext4 rw,nodev,nosuid,noexec,relatime 0 0",
                stderr="",
                code=0
            )
        )
    )

    assert result.status == "PASSED"
    assert result.message == "/tmp is properly configured"


@pytest.mark.filesystem
def test_partition_unexpected_fstype() -> None:
    result = check_filesystem_partition(
        rule_id="filesystem.partition",
        control="Ensure /tmp is a separate partition",
        params={
            "partition": "/tmp",
            "fstype": ["ext4", "xfs"],
            "options": ["nodev", "nosuid", "noexec"]
        },
        executor=MockExecutor(
            lambda argv, **kwargs: ExecutionResult(
                stdout="/tmp ext3 rw,nodev,nosuid,noexec,relatime 0 0",
                stderr="",
                code=0
            )
        )
    )

    assert result.status == "FAILED"
    assert result.message == "/tmp is mounted with an unexpected filesystem type"


@pytest.mark.filesystem
def test_partition_unexpected_options() -> None:
    result = check_filesystem_partition(
        rule_id="filesystem.partition",
        control="Ensure /tmp is a separate partition",
        params={
            "partition": "/tmp",
            "fstype": ["ext4", "xfs"],
            "options": ["nodev", "nosuid", "noexec"]
        },
        executor=MockExecutor(
            lambda argv, **kwargs: ExecutionResult(
                stdout="/tmp ext4 rw,nosuid,relatime 0 0",
                stderr="",
                code=0
            )
        )
    )

    assert result.status == "FAILED"
    assert result.message == "/tmp is mounted with unexpected options"


@pytest.mark.filesystem
def test_partition_empty_param() -> None:
    result = check_filesystem_partition(
        rule_id="filesystem.partition",
        control="Ensure /tmp is a separate partition",
        params={
            "partition": "",
            "fstype": ["ext4", "xfs"],
            "options": ["nodev", "nosuid", "noexec"]
        },
        executor=MockExecutor(
            lambda argv, **kwargs: ExecutionResult(
                stdout="",
                stderr="",
                code=0
            )
        )
    )

    assert result.status == "ERROR"
    assert result.message == "params.partition is empty"


@pytest.mark.filesystem
def test_partition_empty_fstype_param() -> None:
    result = check_filesystem_partition(
        rule_id="filesystem.partition",
        control="Ensure /tmp is a separate partition",
        params={
            "partition": "/tmp",
            "fstype": [],
            "options": ["nodev", "nosuid", "noexec"]
        },
        executor=MockExecutor(
            lambda argv, **kwargs: ExecutionResult(
                stdout="",
                stderr="",
                code=0
            )
        )
    )

    assert result.status == "ERROR"
    assert result.message == "params.fstype is empty"


@pytest.mark.filesystem
def test_partition_empty_options_param() -> None:
    result = check_filesystem_partition(
        rule_id="filesystem.partition",
        control="Ensure /tmp is a separate partition",
        params={
            "partition": "/tmp",
            "fstype": ["ext4", "xfs"],
            "options": []
        },
        executor=MockExecutor(
            lambda argv, **kwargs: ExecutionResult(
                stdout="",
                stderr="",
                code=0
            )
        )
    )

    assert result.status == "ERROR"
    assert result.message == "params.options is empty"


@pytest.mark.filesystem
def test_partition_no_information() -> None:
    result = check_filesystem_partition(
        rule_id="filesystem.partition",
        control="Ensure /tmp is a separate partition",
        params={
            "partition": "/tmp",
            "fstype": ["ext4", "xfs"],
            "options": ["nodev", "nosuid", "noexec"]
        },
        executor=MockExecutor(
            lambda argv, **kwargs: ExecutionResult(
                stdout="",
                stderr="",
                code=1
            )
        )
    )

    assert result.status == "SKIPPED"
    assert result.message == "Unable to determine mount information for /tmp"
