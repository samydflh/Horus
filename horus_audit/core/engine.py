from dataclasses import dataclass

from jinja2 import Environment, FileSystemLoader, StrictUndefined

import horus_audit.controls
from horus_audit.config import config
from horus_audit.core.executor import Executor, LocalExecutor
from horus_audit.core.os_info import detect_os, OSInfo
from horus_audit.core.registry import registry
from horus_audit.core.result import ControlResult


logger = config.get_logger(__name__)


@dataclass
class Summary:
    total: int
    passed: int
    failed: int
    warnings: int
    skipped: int
    errors: int


@dataclass
class Report:
    os_info: OSInfo
    results: list[ControlResult]
    summary: Summary


def run_local_audit(
    os_info: OSInfo | None = None,
    executor: Executor | None = None,
    vars: dict | None = None
) -> Report:
    """
    Run a local audit on the host using Python controls and Jinja rendering.

    Args:
        os_info (OSInfo | None, optional): Detected OS info. Defaults to None.
        executor (Executor | None, optional): Subprocess-based executor. Defaults to None.
        vars (dict | None, optional): Optional variables. Defaults to None.

    Returns:
        Report: Structured audit report.
    """

    os_info = os_info or detect_os()
    executor = executor or LocalExecutor()
    vars = vars or {}

    logger.info(
        "Starting local audit for "
        f"{os_info.name} {os_info.version} "
        f"(distro_id={os_info.distro_id}, family={os_info.family})"
    )

    env = _create_env()

    templates = [
        "base/filesystem.j2",
        "base/kernel.j2",
        "base/services.j2"
    ]
    results = []

    for template in templates:
        try:
            template = env.get_template(template)

        except Exception:
            logger.info(f"No template for tier: {template} (skipping)")
            continue

        try:
            template.render(
                os=os_info,
                vars=vars,
                executor=executor,
                results=results
            )

        except Exception as e:
            logger.error(f"Rendering error in template {template}: {e}")
            results.append(
                ControlResult.error_(
                    id=f"TPL::{template}",
                    message=f"Template rendering error: {e}",
                    details=str(e)
                )
            )

    summary = Summary(
        total=len(results),
        passed=sum(1 for result in results if result.status == "PASSED"),
        failed=sum(1 for result in results if result.status == "FAILED"),
        warnings=sum(1 for result in results if result.status == "WARNING"),
        skipped=sum(1 for result in results if result.status == "SKIPPED"),
        errors=sum(1 for result in results if result.status == "ERROR")
    )

    logger.info(
        "Audit completed: "
        f"total={summary.total}, "
        f"passed={summary.passed}, "
        f"failed={summary.failed}, "
        f"warnings={summary.warnings}, "
        f"skipped={summary.skipped}, "
        f"errors={summary.errors}"
    )

    return Report(os_info=os_info, results=results, summary=summary)


def _create_env() -> Environment:
    paths = [config.default_template_dir]
    loader = FileSystemLoader([str(path) for path in paths])

    env = Environment(
        loader=loader,
        undefined=StrictUndefined,
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
        extensions=["jinja2.ext.do"]
    )
    env.globals.update(registry.as_jinja_globals())

    return env
