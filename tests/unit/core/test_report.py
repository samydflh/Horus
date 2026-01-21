from pathlib import Path

import pytest

from horus_audit.core.report import build_report, render_report
from horus_audit.core.result import ControlResult
from horus_audit.core.rule import Policy


@pytest.mark.report
def test_report_render(tmp_path: Path) -> None:
    template_dir = tmp_path / "templates"
    template_dir.mkdir()

    (template_dir / "default.j2").write_text(
        "Total PASSED={{ report.summary['PASSED'] }}",
        encoding="utf-8"
    )

    policy = Policy(
        category="Unit tests",
        rules=[]
    )

    results = [
        ControlResult.passed_(rule_id="R1", control="Test control", message="Passed"),
        ControlResult.failed_(rule_id="R2", control="Test control", message="Failed")
    ]

    context = build_report(policy=policy, results=results)

    output = render_report(
        context,
        template_dir=str(template_dir)
    )
    assert "PASSED=1" in output
