from pathlib import Path

import pytest
from pytest import MonkeyPatch

from horus_audit.core.exceptions import PolicyError
from horus_audit.core.yaml_loader import load_policy


@pytest.mark.yaml_loader
def test_load_policy(monkeypatch: MonkeyPatch) -> None:
    yaml_content = """
category: Filesystem

rules:
  - rule_id: filesystem.partition
    title: Ensure /tmp is separate
    params:
      partition: /tmp
      fstype: tmpfs
      options: nosuid,nodev,noexec
"""

    monkeypatch.setattr(Path, "exists", lambda self: True)
    monkeypatch.setattr(
        Path,
        "read_text",
        lambda self, encoding=None: yaml_content
    )

    policy = load_policy(Path("policy.yaml"))
    assert policy.category == "Filesystem"
    assert len(policy.rules) == 1

    rule = policy.rules[0]
    assert rule.rule_id == "filesystem.partition"
    assert rule.params["partition"] == "/tmp"
    assert rule.params["fstype"] == "tmpfs"
    assert rule.params["options"] == "nosuid,nodev,noexec"


@pytest.mark.yaml_loader
def test_load_policy_file_not_found(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(Path, "exists", lambda self: False)

    with pytest.raises(PolicyError):
        load_policy(Path("policy.yaml"))


@pytest.mark.yaml_loader
def test_load_policy_invalid_yaml(monkeypatch: MonkeyPatch) -> None:
    def read_text(self, encoding=None):
        raise Exception("YAML error")

    monkeypatch.setattr(Path, "exists", lambda self: True)
    monkeypatch.setattr(Path, "read_text", read_text)

    with pytest.raises(PolicyError):
        load_policy(Path("policy.yaml"))


@pytest.mark.yaml_loader
def test_load_policy_mapping_error(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(Path, "exists", lambda self: True)
    monkeypatch.setattr(
        Path,
        "read_text",
        lambda self, encoding=None: "- YAML content\n"
    )

    with pytest.raises(PolicyError):
        load_policy(Path("policy.yaml"))


@pytest.mark.yaml_loader
def test_load_policy_format_error(monkeypatch: MonkeyPatch) -> None:
    yaml_content = """
category: Filesystem
"""

    monkeypatch.setattr(Path, "exists", lambda self: True)
    monkeypatch.setattr(
        Path,
        "read_text",
        lambda self, encoding=None: yaml_content
    )

    with pytest.raises(PolicyError):
        load_policy(Path("policy.yaml"))


@pytest.mark.yaml_loader
def test_load_policy_parsing_error(monkeypatch: MonkeyPatch) -> None:
    yaml_content = """
category: Filesystem

rules:
  - rule_id: filesystem.partition
"""

    monkeypatch.setattr(Path, "exists", lambda self: True)
    monkeypatch.setattr(
        Path,
        "read_text",
        lambda self, encoding=None: yaml_content
    )

    with pytest.raises(PolicyError):
        load_policy(Path("policy.yaml"))
