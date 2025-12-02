from pathlib import Path
import tempfile

import pytest
from pytest import MonkeyPatch

from horus_audit.controls.base import (
    check_file_exists,
    check_file_permissions,
    check_partition
)
from horus_audit.core.executor import ExecutionResult, LocalExecutor


@pytest.mark.filesystem
def test_check_partition_passed(monkeypatch: MonkeyPatch) -> None:
    mock_executor = LocalExecutor()

    def mock_run(command: str) -> ExecutionResult:
        return ExecutionResult(
            code=0,
            stdout="ext4 nodev,nosuid",
            stderr=""
        )

    monkeypatch.setattr(mock_executor, "run", mock_run)

    result = check_partition(
        mount="/var",
        expected_fstype=("ext4", "xfs"),
        expected_options=("nodev", "nosuid"),
        executor=mock_executor,
        control_name="test_partition"
    )

    assert result.status == "PASSED"
    assert result.name == "test_partition"
    assert result.message == "/var is a separate partition"


@pytest.mark.filesystem
def test_check_partition_failed(monkeypatch: MonkeyPatch) -> None:
    mock_executor = LocalExecutor()

    def mock_run(command: str) -> ExecutionResult:
        return ExecutionResult(
            code=1,
            stdout="",
            stderr=""
        )

    monkeypatch.setattr(mock_executor, "run", mock_run)

    result = check_partition(
        mount="/non_existent",
        expected_fstype=("ext4", "xfs"),
        expected_options=("nodev", "nosuid", "noexec"),
        executor=mock_executor,
        control_name="test_partition"
    )

    assert result.status == "FAILED"
    assert result.name == "test_partition"
    assert result.message == "Cannot find /non_existent partition"


@pytest.mark.filesystem
def test_check_partition_warning_fstype(monkeypatch: MonkeyPatch) -> None:
    mock_executor = LocalExecutor()

    def mock_run(command: str) -> ExecutionResult:
        return ExecutionResult(
            code=0,
            stdout="ext2 nodev,nosuid",
            stderr=""
        )

    monkeypatch.setattr(mock_executor, "run", mock_run)

    result = check_partition(
        mount="/var",
        expected_fstype=("ext4",),
        expected_options=("nodev", "nosuid"),
        executor=mock_executor,
        control_name="test_partition"
    )

    assert result.status == "WARNING"
    assert result.name == "test_partition"
    assert result.message == "/var has ext2 filesystem, expected ext4"


@pytest.mark.filesystem
def test_check_partition_warning_options(monkeypatch: MonkeyPatch) -> None:
    mock_executor = LocalExecutor()

    def mock_run(command: str) -> ExecutionResult:
        return ExecutionResult(
            code=0,
            stdout="ext4 nodev",
            stderr=""
        )

    monkeypatch.setattr(mock_executor, "run", mock_run)

    result = check_partition(
        mount="/tmp",
        expected_fstype=("ext4",),
        expected_options=("nodev", "nosuid", "noexec"),
        executor=mock_executor,
        control_name="test_partition"
    )

    assert result.status == "WARNING"
    assert result.name == "test_partition"
    assert result.message == "/tmp does not include options nosuid, noexec"


@pytest.mark.filesystem
def test_check_file_exists_passed() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_file = Path(tmp_dir) / "tmp_file_1"
        tmp_file.touch()

        result = check_file_exists(str(tmp_file), control_name="test_file_exists")

        assert result.status == "PASSED"
        assert result.name == "test_file_exists"
        assert result.message == f"{tmp_file} exists"


@pytest.mark.filesystem
def test_check_file_exists_failed() -> None:
    non_existent_file = "/non/existent/filepath"
    result = check_file_exists(non_existent_file, control_name="test_file_exists")

    assert result.status == "FAILED"
    assert result.name == "test_file_exists"
    assert result.message == f"{non_existent_file} does not exist"


@pytest.mark.filesystem
def test_check_file_permissions_passed() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_file = Path(tmp_dir) / "tmp_file_2"
        tmp_file.touch(mode=0o600)

        result = check_file_permissions(
            str(tmp_file),
            "755",
            control_name="test_file_permissions"
        )

        assert result.status == "PASSED"
        assert result.name == "test_file_permissions"
        assert "permissions are compliant" in result.message


@pytest.mark.filesystem
def test_check_file_permissions_failed() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_file = Path(tmp_dir) / "tmp_file_3"
        tmp_file.touch(mode=0o644)

        result = check_file_permissions(
            str(tmp_file),
            "600",
            control_name="test_file_permissions"
        )

        assert result.status == "FAILED"
        assert result.name == "test_file_permissions"
        assert "has permissions 644" in result.message
        assert "expected 600" in result.message


@pytest.mark.filesystem
def test_check_file_permissions_warning() -> None:
    non_existent_file = "/non/existent/filepath"

    result = check_file_permissions(
        non_existent_file,
        "600",
        control_name="test_file_permissions"
    )

    assert result.status == "WARNING"
    assert result.name == "test_file_permissions"
    assert result.message == f"{non_existent_file} not found"


@pytest.mark.filesystem
def test_check_file_permissions_skipped(monkeypatch: MonkeyPatch) -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_file = Path(tmp_dir) / "tmp_file_4"
        tmp_file.touch()

        def mock_permission_error(path):
            raise PermissionError("No access")

        monkeypatch.setattr("os.stat", mock_permission_error)

        result = check_file_permissions(
            str(tmp_file),
            "600",
            control_name="test_file_permissions"
        )

        assert result.status == "SKIPPED"
        assert result.name == "test_file_permissions"
        assert result.message == f"No permission to access {tmp_file}"
