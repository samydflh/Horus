from dataclasses import dataclass
from typing import Literal


@dataclass
class ControlResult:
    rule_id: str
    control: str
    status: Literal["PASSED", "FAILED", "WARNING", "SKIPPED", "ERROR"]
    message: str

    @classmethod
    def passed_(cls, *, rule_id: str, control: str, message: str) -> "ControlResult":
        return cls(rule_id=rule_id, control=control, status="PASSED", message=message)

    @classmethod
    def failed_(cls, *, rule_id: str, control: str, message: str) -> "ControlResult":
        return cls(rule_id=rule_id, control=control, status="FAILED", message=message)

    @classmethod
    def warning_(cls, *, rule_id: str, control: str, message: str) -> "ControlResult":
        return cls(rule_id=rule_id, control=control, status="WARNING", message=message)

    @classmethod
    def skipped_(cls, *, rule_id: str, control: str, message: str) -> "ControlResult":
        return cls(rule_id=rule_id, control=control, status="SKIPPED", message=message)

    @classmethod
    def error_(cls, *, rule_id: str, control: str, message: str) -> "ControlResult":
        return cls(rule_id=rule_id, control=control, status="ERROR", message=message)
