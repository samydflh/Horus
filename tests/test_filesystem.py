from pathlib import Path
import tempfile

import pytest
from pytest import MonkeyPatch

from horus_audit.controls.base import check_file_exists, check_file_permissions


@pytest.mark.filesystem
def test_check_file_exists_passed() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_file = Path(tmp_dir) / "tmp_file_1"
        tmp_file.touch()

        result = check_file_exists(str(tmp_file), control_name="test_file_exists")

        assert result.status == "PASSED"
        assert result.name == "test_file_exists"
        assert f"{tmp_file} exists" in result.message


@pytest.mark.filesystem
def test_check_file_exists_failed() -> None:
    non_existent_file = "/non/existent/filepath"
    result = check_file_exists(non_existent_file, control_name="test_file_exists")

    assert result.status == "FAILED"
    assert result.name == "test_file_exists"
    assert f"{non_existent_file} does not exist" in result.message


@pytest.mark.filesystem
def test_check_file_permissions_passed() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_file = Path(tmp_dir) / "tmp_file_2"
        tmp_file.touch(mode=0o755)

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
    assert f"{non_existent_file} not found" in result.message


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
        assert f"No permission to access {tmp_file}" in result.message
