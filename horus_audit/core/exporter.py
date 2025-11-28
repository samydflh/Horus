from dataclasses import asdict, is_dataclass
import json
from pathlib import Path
from typing import Any, Protocol

from horus_audit.core.engine import Report


class Exporter(Protocol):
    def export(self, report: Report) -> Any:
        ...


class JSONExporter:
    def __init__(self, indent: int = 2) -> None:
        self.indent = indent

    def export(self, report: Report) -> str:
        """
        Convert the report to a JSON string.

        Args:
            report (Report): Produced audit report.

        Returns:
            str: Exported JSON string.
        """

        data = _serialize(report)
        return json.dumps(data, indent=self.indent)


def export(report: Report, format: str) -> Any:
    """
    Convert a report to any format.

    Args:
        report (Report): Produced audit report.
        format (str): Export format.

    Returns:
        Any: Exported data.
    """

    format = format.lower()

    if format not in _exporters:
        raise ValueError(f"Unknown export format: {format}")

    exporter = _exporters[format]

    return exporter.export(report)


def write(report: Report, output_path: Path, format: str) -> None:
    """
    Write the exported report to a file.

    Args:
        report (Report): Produced audit report.
        output_path (Path): JSON file path.
        format (str): Export format.
    """

    result = export(report, format)

    if isinstance(result, str):
        output_path.write_text(result, encoding="utf-8")
    elif isinstance(result, bytes):
        output_path.write_bytes(result)
    else:
        raise TypeError(
            f"Exporting to '{format}' returned unsupported type: {type(result)}"
        )


def _serialize(data: Any) -> Any:
    """
    Serialize the object to any format.

    Args:
        data (Any): Data to serialize.

    Returns:
        Any: Serialized object.
    """

    # Basic types
    if data is None or isinstance(data, (str, int, float, bool)):
        return data

    # Path
    if isinstance(data, Path):
        return str(data)

    # List or tuple
    if isinstance(data, (list, tuple)):
        return [_serialize(obj) for obj in data]

    # Dictionary
    if isinstance(data, dict):
        return {key: _serialize(value) for key, value in data.items()}

    # Dataclass
    if is_dataclass(data):
        return _serialize(asdict(data))

    # Fallback: string object
    return str(data)


# Exporter registry
_exporters = {
    "json": JSONExporter()
}
