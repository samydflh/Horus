from dataclasses import dataclass, field
from typing import Any


@dataclass
class Rule:
    rule_id: str
    title: str
    params: dict[str, Any] = field(default_factory=dict)


@dataclass
class Policy:
    category: str
    rules: list[Rule]
