from dataclasses import dataclass, field
from typing import Any, Literal


Status = Literal["PASSED", "FAILED", "WARNING", "SKIPPED", "ERROR"]


@dataclass
class ControlResult:
    name: str
    status: Status
    message: str
    details: str | None = None
    remediation: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def passed_(cls, name: str, message: str, **kwargs: Any) -> "ControlResult":
        return cls(name=name, status="PASSED", message=message, **kwargs)

    @classmethod
    def failed_(cls, name: str, message: str, **kwargs: Any) -> "ControlResult":
        return cls(name=name, status="FAILED", message=message, **kwargs)

    @classmethod
    def warning_(cls, name: str, message: str, **kwargs: Any) -> "ControlResult":
        return cls(name=name, status="WARNING", message=message, **kwargs)

    @classmethod
    def skipped_(cls, name: str, message: str, **kwargs: Any) -> "ControlResult":
        return cls(name=name, status="SKIPPED", message=message, **kwargs)

    @classmethod
    def error_(cls, name: str, message: str, **kwargs: Any) -> "ControlResult":
        return cls(name=name, status="ERROR", message=message, **kwargs)
