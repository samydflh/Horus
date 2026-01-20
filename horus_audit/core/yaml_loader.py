from pathlib import Path
from typing import Any

import yaml

from horus_audit.core.exceptions import PolicyError
from horus_audit.core.rule import Policy, Rule


def load_policy(path: Path) -> Policy:
    """
    Load an external policy.

    Args:
        path (Path): Policy file.

    Returns:
        Policy: YAML policy.

    Raises:
        PolicyError: Policy issues.
    """

    if not path.exists():
        raise PolicyError(f"Policy file not found: {path}")

    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise PolicyError(f"Invalid YAML: {exc}")

    if not isinstance(raw, dict):
        raise PolicyError("Policy root has to be a mapping")

    category = raw.get("category")
    rules_raw = raw.get("rules")

    if not isinstance(category, str) or not category:
        raise PolicyError("Unexpected 'category' format")

    if not isinstance(rules_raw, list) or not rules_raw:
        raise PolicyError("Unexpected 'rules' format")

    rules = []

    for i, rule in enumerate(rules_raw):
        rules.append(_parse_rule(i, rule))

    return Policy(category=category, rules=rules)


def _parse_rule(i: int, rule: dict[str, Any]) -> Rule:
    if not isinstance(rule, dict):
        raise PolicyError(f"rules[{i}] has to be a mapping")

    rule_id = rule.get("rule_id")
    control = rule.get("control")
    params = rule.get("params", {})

    if not isinstance(rule_id, str) or not rule_id:
        raise PolicyError(f"No rules[{i}].rule_id")

    if not isinstance(control, str) or not control:
        raise PolicyError(f"No rules[{i}].control")

    if not isinstance(params, dict):
        raise PolicyError(f"rules[{i}].params has to be a mapping")

    return Rule(
        rule_id=rule_id,
        control=control,
        params=params
    )
