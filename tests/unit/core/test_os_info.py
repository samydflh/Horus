import pytest
from pytest import MonkeyPatch

from horus_audit.core.os_info import OSInfo, detect_os


class Logger:
    def info(self, *a, **k): pass
    def warning(self, *a, **k): pass
    def error(self, *a, **k): pass


@pytest.mark.os_info
def test_detect_os(monkeypatch: MonkeyPatch) -> None:
    class Distro:
        @staticmethod
        def id():
            return "ubuntu"

        @staticmethod
        def name():
            return "Ubuntu"

        @staticmethod
        def version(pretty=True, best=True):
            return "24.04.3 (noble)"

        @staticmethod
        def major_version():
            return "24"

        @staticmethod
        def like():
            return "debian"

    class Uname:
        def __init__(self):
            self.release = "6.5.0-28-generic"
            self.machine = "x86_64"
            self.node = "test-ubuntu"

    monkeypatch.setattr(
        "horus_audit.core.os_info.logger",
        Logger()
    )
    monkeypatch.setattr(
        "horus_audit.core.os_info.distro",
        Distro,
        raising=True
    )
    monkeypatch.setattr(
        "horus_audit.core.os_info.platform.uname",
        lambda: Uname()
    )

    os_info = detect_os()

    assert isinstance(os_info, OSInfo)

    assert os_info.distro_id== "ubuntu"
    assert os_info.name == "Ubuntu"
    assert os_info.version == "24.04.3 (noble)"
    assert os_info.major_version == "24"
    assert os_info.family == "debian"
    assert os_info.kernel_version == "6.5.0-28-generic"
    assert os_info.architecture == "x86_64"
    assert os_info.hostname == "test-ubuntu"


@pytest.mark.os_info
def test_detect_os_fallback(monkeypatch: MonkeyPatch) -> None:
    class Distro:
        @staticmethod
        def id():
            return "weirdos"

        @staticmethod
        def name():
            return "WeirdOS"

        @staticmethod
        def version(pretty=True, best=True):
            return "1.0"

        @staticmethod
        def major_version():
            return "1"

        @staticmethod
        def like():
            return ""

    class Uname:
        def __init__(self):
            self.release = "5.15.0-generic"
            self.machine = "aarch64"
            self.node = "test-hostname"

    monkeypatch.setattr(
        "horus_audit.core.os_info.logger",
        Logger()
    )
    monkeypatch.setattr(
        "horus_audit.core.os_info.distro",
        Distro,
        raising=True
    )
    monkeypatch.setattr(
        "horus_audit.core.os_info.platform.uname",
        lambda: Uname()
    )

    os_info = detect_os()

    assert isinstance(os_info, OSInfo)

    assert os_info.distro_id == "weirdos"
    assert os_info.name == "WeirdOS"
    assert os_info.version == "1.0"
    assert os_info.major_version == "1"
    assert os_info.family == "weirdos"
    assert os_info.kernel_version == "5.15.0-generic"
    assert os_info.architecture == "aarch64"
    assert os_info.hostname == "test-hostname"
