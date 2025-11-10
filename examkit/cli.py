"""
Command-line interface for ExamKit using Typer.
"""

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from examkit.config import ExamKitConfig
from examkit.logging_utils import setup_logging
from examkit.ingestion.ingest import ingest_pipeline
from examkit.synthesis.composer import build_pipeline
from examkit.reports.export import generate_report

app = typer.Typer(
    name="examkit",
    help="ExamKit - Production-grade exam preparation toolkit (offline, local-only)",
    add_completion=False
)
console = Console()


@app.command()
def ingest(
    manifest: Path = typer.Option(
        ...,
        "--manifest",
        "-m",
        help="Path to manifest.json describing input files",
        exists=True,
        file_okay=True,
        dir_okay=False
    ),
    cache_dir: Path = typer.Option(
        Path("cache"),
        "--cache",
        "-c",
        help="Directory for cached/processed files"
    ),
    log_level: str = typer.Option("INFO", "--log-level", "-l", help="Logging level")
) -> None:
    """
    Run the ingestion pipeline to preprocess input files and populate the cache.
    
    Loads the manifest, invokes the ingestion pipeline to process videos, transcripts,
    slides, and exam files, and writes processed artifacts to the specified cache
    directory while printing status to the console. On failure the function logs the
    error and exits the process with code 1.
     
    Raises:
    	typer.Exit: Exits with code 1 when ingestion fails.
    """
    logger = setup_logging(level=log_level, log_file=Path("logs/ingest.log"))
    logger.info("Starting ingestion pipeline")

    try:
        # Load manifest
        with open(manifest, "r") as f:
            manifest_data = json.load(f)

        # Run ingestion
        result = ingest_pipeline(manifest_data, cache_dir, logger)

        console.print("\n[bold green]✓[/bold green] Ingestion complete!", style="bold")
        console.print(f"Processed files saved to: {cache_dir}")
        console.print(f"Normalized manifest: {result['normalized_manifest']}")

    except Exception as e:
        logger.error(f"Ingestion failed: {e}", exc_info=True)
        console.print(f"[bold red]✗[/bold red] Error: {e}", style="bold red")
        raise typer.Exit(code=1)


@app.command()
def build(
    config: Path = typer.Option(
        Path("config/config.yml"),
        "--config",
        "-c",
        help="Path to config.yml",
        exists=True
    ),
    out: Path = typer.Option(
        Path("out/output.pdf"),
        "--out",
        "-o",
        help="Output PDF path"
    ),
    session_id: str = typer.Option(
        "default",
        "--session",
        "-s",
        help="Session identifier for tracking"
    ),
    offline: bool = typer.Option(
        True,
        "--offline/--online",
        help="Enforce offline mode (no network calls)"
    ),
    log_level: str = typer.Option("INFO", "--log-level", "-l", help="Logging level")
) -> None:
    """
    Build an exam-ready PDF for a session using the provided configuration and write outputs to the specified path.
    
    Prints the generated PDF, citations, coverage, and notes paths to the console. Exits with code 1 on error.
    """
    logger = setup_logging(level=log_level, log_file=Path("logs/build.log"))
    logger.info(f"Starting build pipeline for session: {session_id}")

    try:
        # Load configuration
        cfg = ExamKitConfig.from_yaml(config)
        cfg.offline = offline

        # Run build
        result = build_pipeline(cfg, session_id, out, logger)

        console.print("\n[bold green]✓[/bold green] Build complete!", style="bold")
        console.print(f"PDF: {result['pdf_path']}")
        console.print(f"Citations: {result['citations_path']}")
        console.print(f"Coverage: {result['coverage_path']}")
        console.print(f"Notes: {result['notes_path']}")

    except Exception as e:
        logger.error(f"Build failed: {e}", exc_info=True)
        console.print(f"[bold red]✗[/bold red] Error: {e}", style="bold red")
        raise typer.Exit(code=1)


@app.command()
def report(
    session: str = typer.Option(
        "default",
        "--session",
        "-s",
        help="Session identifier"
    ),
    open_coverage: bool = typer.Option(
        False,
        "--open",
        help="Open coverage CSV after generation"
    ),
    log_level: str = typer.Option("INFO", "--log-level", "-l", help="Logging level")
) -> None:
    """
    Generate and display coverage and QA report for a session.

    Shows topic coverage, source utilization, QA checks, and any warnings.
    """
    logger = setup_logging(level=log_level)
    logger.info(f"Generating report for session: {session}")

    try:
        report_data = generate_report(session, logger)

        # Display coverage table
        table = Table(title=f"Coverage Report - {session}", show_header=True)
        table.add_column("Topic", style="cyan")
        table.add_column("Coverage %", justify="right", style="green")
        table.add_column("Sources", justify="right")

        for topic in report_data.get("coverage", []):
            table.add_row(
                topic["name"],
                f"{topic['coverage']:.1f}%",
                str(topic["source_count"])
            )

        console.print(table)

        # Display QA summary
        qa = report_data.get("qa", {})
        console.print(f"\n[bold]QA Summary:[/bold]")
        console.print(f"  Formulas checked: {qa.get('formulas_checked', 0)}")
        console.print(f"  Links verified: {qa.get('links_verified', 0)}")
        console.print(f"  Warnings: {qa.get('warnings', 0)}")

        if open_coverage and report_data.get("coverage_path"):
            import subprocess
            subprocess.run(["open", report_data["coverage_path"]])

    except Exception as e:
        logger.error(f"Report generation failed: {e}", exc_info=True)
        console.print(f"[bold red]✗[/bold red] Error: {e}", style="bold red")
        raise typer.Exit(code=1)


@app.command()
def cache(
    action: str = typer.Argument(
        ...,
        help="Action to perform (clear)"
    )
) -> None:
    """
    Manage the local cache directory for the CLI.
    
    When `action` is "clear", delete the cache directory if it exists and recreate it; if the directory does not exist, print a warning. For any other `action`, print an error listing available actions and exit with a non-zero status.
    
    Parameters:
        action (str): Action to perform. Supported value: "clear".
    """
    if action == "clear":
        cache_dir = Path("cache")
        if cache_dir.exists():
            import shutil
            shutil.rmtree(cache_dir)
            cache_dir.mkdir(parents=True, exist_ok=True)
            console.print("[bold green]✓[/bold green] Cache cleared successfully")
        else:
            console.print("[yellow]Cache directory does not exist[/yellow]")
    else:
        console.print(f"[bold red]Unknown action:[/bold red] {action}")
        console.print("Available actions: clear")
        raise typer.Exit(code=1)


def main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()