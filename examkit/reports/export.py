"""
Report export utilities.
"""

import logging
from pathlib import Path
from typing import Any, Dict

from examkit.utils.io_utils import read_json, read_text


def generate_report(session_id: str, logger: logging.Logger) -> Dict[str, Any]:
    """
    Generate comprehensive report for a session.

    Args:
        session_id: Session identifier.
        logger: Logger instance.

    Returns:
        Dictionary with report data.
    """
    out_dir = Path("out")

    report = {
        "session_id": session_id,
        "coverage": [],
        "qa": {},
        "citations": [],
        "coverage_path": None
    }

    # Load coverage data
    coverage_path = out_dir / f"{session_id}_coverage.csv"
    if coverage_path.exists():
        import pandas as pd
        df = pd.read_csv(coverage_path)
        report["coverage"] = df.to_dict("records")
        report["coverage_path"] = str(coverage_path)

    # Load citations
    citations_path = out_dir / f"{session_id}_citations.json"
    if citations_path.exists():
        report["citations"] = read_json(citations_path)

    # Load notes for QA
    notes_path = out_dir / f"{session_id}_notes.md"
    if notes_path.exists():
        from examkit.qa.checks import run_all_checks
        notes_content = read_text(notes_path)
        qa_results = run_all_checks(notes_content, logger=logger)

        report["qa"] = {
            "formulas_checked": qa_results["formulas"]["total_formulas"],
            "links_verified": qa_results["links"]["total_links"],
            "citations_found": qa_results["citations"]["total_citations"],
            "warnings": sum([
                len(qa_results["formulas"].get("invalid_formulas", [])),
                len(qa_results["links"].get("broken_links", []))
            ])
        }

    return report


def export_report_text(report: Dict[str, Any], output_path: Path) -> None:
    """
    Export report as text file.

    Args:
        report: Report dictionary.
        output_path: Output path for text file.
    """
    lines = [
        f"ExamKit Report - {report['session_id']}",
        "=" * 60,
        ""
    ]

    # Coverage summary
    if report["coverage"]:
        lines.append("Topic Coverage:")
        lines.append("-" * 60)
        for item in report["coverage"]:
            lines.append(f"  {item['name']}: {item['coverage_percentage']:.1f}% ({item['chunk_count']} chunks)")
        lines.append("")

    # QA summary
    if report["qa"]:
        lines.append("Quality Assurance:")
        lines.append("-" * 60)
        lines.append(f"  Formulas checked: {report['qa']['formulas_checked']}")
        lines.append(f"  Links verified: {report['qa']['links_verified']}")
        lines.append(f"  Citations found: {report['qa']['citations_found']}")
        lines.append(f"  Warnings: {report['qa']['warnings']}")
        lines.append("")

    # Citations summary
    if report["citations"]:
        lines.append(f"Total Citations: {len(report['citations'])}")
        lines.append("")

    from examkit.utils.io_utils import write_text
    write_text("\n".join(lines), output_path)


def export_report_json(report: Dict[str, Any], output_path: Path) -> None:
    """
    Export report as JSON file.

    Args:
        report: Report dictionary.
        output_path: Output path for JSON file.
    """
    from examkit.utils.io_utils import write_json
    write_json(report, output_path)
