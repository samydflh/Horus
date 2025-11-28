import os
from pathlib import Path
import sys

from rich import box
from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text
import typer

from horus_audit import __version__
from horus_audit.core.engine import run_local_audit, Summary
from horus_audit.core.exporter import write
from horus_audit.core.os_info import detect_os, OSInfo
from horus_audit.core.result import ControlResult


app = typer.Typer(
    name="horus",
    help="Horus — Linux security auditing tool based on CIS benchmarks.",
    context_settings={"help_option_names": ["--help"]},
    add_completion=False
)
console = Console()


@app.command(add_help_option=False)
def audit(
    context: typer.Context,
    json_file: str = typer.Option(
        None,
        "--json",
        help="Write the report to a JSON file.",
        metavar="JSON_FILE"
    ),
    help: bool = typer.Option(
        False,
        "--help",
        help="Show help.",
        is_eager=True
    )
) -> None:
    """
    Run a local audit on the host.
    """

    if help:
        print(context.get_help())
        raise typer.Exit()

    try:
        console.print()
        os_info = detect_os()

        _print_header(os_info)

        report = run_local_audit(os_info=os_info)

        _print_results(report.results)
        _print_summary(report.summary)

        console.print()

        if json_file:
            write(report, Path(json_file), format="json")
            console.print(f"✅ JSON report: {json_file}", style="green")
            console.print()

    except KeyboardInterrupt:
        console.print("⚠️ Program interrupted by the user", style="yellow")
        console.print()
        raise typer.Exit(130)

    except Exception:
        console.print_exception()
        console.print()
        raise typer.Exit(1)


def _print_header(os_info: OSInfo) -> None:
    program_items = [
        ("Program version", f"Horus {__version__}"),
        ("Execution mode", "Privileged" if _is_privileged() else "Non-privileged")
    ]
    os_items = [
        ("Operating system", f"{os_info.name} {os_info.version}"),
        ("Kernel version", os_info.kernel_version),
        ("Architecture", os_info.architecture),
        ("Hostname", os_info.hostname)
    ]

    items = program_items + os_items
    max_width = _compute_max_width(items)

    lines = (
        [_format_line(label, value, max_width) for label, value in program_items]
        + [""]
        + [_format_line(label, value, max_width) for label, value in os_items]
    )

    header_text = Text("\n".join(lines), style="white")

    console.print(
        Panel(
            header_text,
            title="[bold cyan]Horus[/bold cyan]",
            title_align="left",
            box=box.ROUNDED,
            border_style="cyan",
            padding=(1, 2)
        )
    )
    console.print()


def _print_results(results: list[ControlResult]) -> None:
    if not results:
        console.print(
            Panel(
                Text("No controls were executed.", style="yellow"),
                title="[bold cyan]Audit results[/bold cyan]",
                title_align="left",
                box=box.ROUNDED,
                border_style="cyan",
                padding=(1, 2)
            )
        )
        console.print()
        sys.exit()

    cis_titles = [result.name for result in results]
    max_length = max(len(cis_id) for cis_id in cis_titles) if cis_titles else 0

    renderables = []

    for result in results:
        padding = " " * (max_length - len(result.name) + 30)

        line = Text()
        line.append(f" {result.name}{padding}", style="bold cyan")
        line.append(_format_status(result.status))

        if result.message:
            line.append("\n")
            line.append(f"  {result.message}", style="dim white")

        renderables.append(line)

    console.print(
        Panel(
            Group(*renderables),
            title="[bold cyan]Audit results[/bold cyan]",
            title_align="left",
            box=box.ROUNDED,
            border_style="cyan",
            padding=(1, 2)
        )
    )
    console.print()


def _print_summary(summary: Summary) -> None:
    summary_items = [
        ("Tests performed", str(summary.total)),
        ("Passed", str(summary.passed)),
        ("Failed", str(summary.failed)),
        ("Warnings", str(summary.warnings)),
        ("Skipped", str(summary.skipped)),
        ("Errors", str(summary.errors))
    ]

    max_width = _compute_max_width(summary_items)
    lines = [_format_line(label, value, max_width) for label, value in summary_items]
    summary_text = Text("\n".join(lines), style="white")

    console.print(
        Panel(
            summary_text,
            title="[bold cyan]Audit summary[/bold cyan]",
            title_align="left",
            box=box.ROUNDED,
            border_style="cyan",
            padding=(1, 2)
        )
    )


def _compute_max_width(items: list[tuple[str, str]]) -> int:
    return max(len(data) for data, _ in items) if items else 0


def _format_status(status: str) -> Text:
    colors = {
        "PASSED": "green",
        "FAILED": "red",
        "WARNING": "yellow",
        "SKIPPED": "blue",
        "ERROR": "magenta"
    }
    return Text(f"[{status}]", style=f"bold {colors.get(status, 'white')}")


def _format_line(data: str, value: str, max_width: int) -> str:
    padding = max(4, max_width - len(data) + 4)
    return f"{data}:{' ' * padding}{value}"


def _is_privileged() -> bool:
    return os.geteuid() == 0


@app.callback(invoke_without_command=True)
def main(
    context: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        help="Show version.",
        is_eager=True
    ),
    help: bool = typer.Option(
        False,
        "--help",
        help="Show help.",
        is_eager=True
    )
) -> None:
    if version:
        console.print(f"Horus {__version__}", style="bold blue")
        raise typer.Exit()

    if help:
        print(context.get_help())
        raise typer.Exit()


if __name__ == "__main__":
    app()
