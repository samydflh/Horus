from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from horus_audit.core.result import ControlResult
from horus_audit.core.rule import Policy


@dataclass
class ReportContext:
    category: str
    generated_at: str
    results: list[ControlResult]
    summary: dict[str, int]
    os_info: Any | None


def build_report(
    *,
    policy: Policy,
    results: list[ControlResult],
    os_info: Any | None = None
) -> ReportContext:
    summary = {
        "PASSED": 0,
        "FAILED": 0,
        "WARNING": 0,
        "SKIPPED": 0,
        "ERROR": 0
    }

    for result in results:
        summary[result.status] += 1

    return ReportContext(
        category=policy.category,
        generated_at=datetime.now(timezone.utc).isoformat() + "Z",
        results=results,
        summary=summary,
        os_info=os_info
    )


def render_report(
    context: ReportContext,
    *,
    template_dir: str,
    template_name: str = "default.j2"
) -> str:
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(enabled_extensions=()),
        enable_async=False
    )
    template = env.get_template(template_name)

    return template.render(report=context)
