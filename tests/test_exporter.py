from dataclasses import dataclass
import json
from pathlib import Path

import pytest
from pytest import MonkeyPatch

from horus_audit.core.engine import Report, Summary
from horus_audit.core.exporter import write, _serialize
from horus_audit.core.os_info import OSInfo
from horus_audit.core.result import ControlResult


@pytest.fixture
def report() -> Report:
    os_info = OSInfo(
        distro_id="ubuntu",
        name="Ubuntu",
        version="24.04 LTS",
        major_version="24",
        family="debian",
        kernel_version="6.8.0-31-generic",
        architecture="x86_64",
        hostname="test-ubuntu"
    )

    results = [
        ControlResult(
            name="Control 1",
            status="PASSED",
            message="Control passed"
        ),
        ControlResult(
            name="Control 2",
            status="FAILED",
            message="Control failed"
        )
    ]

    summary = Summary(
        total=1,
        passed=1,
        failed=1,
        warnings=0,
        skipped=0,
        errors=0
    )

    return Report(
        os_info=os_info,
        results=results,
        summary=summary
    )


@pytest.mark.exporter
def test_serialize_basic_types() -> None:
    assert _serialize(None) is None
    assert _serialize("abc") == "abc"
    assert _serialize(1) == 1
    assert _serialize(1.5) == 1.5
    assert _serialize(True) is True


@pytest.mark.exporter
def test_serialize_path() -> None:
    path = Path("/tmp/file")
    assert _serialize(path) == "/tmp/file"


@pytest.mark.exporter
def test_serialize_lists() -> None:
    list_str = ["a" ,"b", "c"]
    assert _serialize(list_str) == list_str

    list_int = [1, 2, 3]
    assert _serialize(list_int) == list_int

    list_paths = [Path("/tmp/file_1"), Path("/tmp/file_2")]
    assert _serialize(list_paths) == ["/tmp/file_1", "/tmp/file_2"]


@pytest.mark.exporter
def test_serialize_tuples() -> None:
    tuple_str = ("a" ,"b", "c")
    assert _serialize(tuple_str) == list(tuple_str)

    tuple_int = (1, 2, 3)
    assert _serialize(tuple_int) == list(tuple_int)

    tuple_paths = (Path("/tmp/file_1"), Path("/tmp/file_2"))
    assert _serialize(tuple_paths) == ["/tmp/file_1", "/tmp/file_2"]


@pytest.mark.exporter
def test_serialize_dictionaries() -> None:
    dict_str = {
        "key_1": "value_1",
        "key_2": "value_2"
    }
    assert _serialize(dict_str) == dict_str

    dict_int = {
        "key_1": 1,
        "key_2": 2
    }
    assert _serialize(dict_int) == dict_int

    dict_multi = {
        "str": "Hello World",
        "int": 42,
        "path": Path("/tmp/file"),
        "list": [True, False]
    }

    assert _serialize(dict_multi) == {
        "str": "Hello World",
        "int": 42,
        "path": "/tmp/file",
        "list": [True, False]
    }


@pytest.mark.exporter
def test_serialize_dataclasses() -> None:
    @dataclass
    class Child:
        id: str
        value: int
        path: Path

    @dataclass
    class Parent:
        name: str
        child: Child
        values: list[int]

    parent = Parent(
        name="root",
        child=Child(
            id="ID_001",
            value=42,
            path=Path("/tmp/file")
        ),
        values=[1, 2, 3]
    )

    result = _serialize(parent)

    assert result == {
        "name": "root",
        "child": {
            "id": "ID_001",
            "value": 42,
            "path": "/tmp/file"
        },
        "values": [1, 2, 3]
    }


@pytest.mark.exporter
def test_write_json(monkeypatch: MonkeyPatch, report: Report) -> None:
    captured_args = {}

    def write_text(self, content: str, encoding: str):
        captured_args["content"] = content
        captured_args["encoding"] = encoding

    monkeypatch.setattr(Path, "write_text", write_text)

    write(report, Path("/tmp/report.json"), "json")
    assert captured_args["encoding"] == "utf-8"

    data = json.loads(captured_args["content"])

    assert "os_info" in data
    assert "results" in data
    assert "summary" in data
