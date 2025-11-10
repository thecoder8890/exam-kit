"""
Report export utilities.
"""

import logging
from pathlib import Path
from typing import Any, Dict

from examkit.utils.io_utils import read_json, read_text


def generate_report(session_id: str, logger: logging.Logger) -> Dict[str, Any]:
    """
    Assemble a session report by collecting coverage CSV, QA notes, and citation JSON from the out/ directory.
    
    Parameters:
        session_id (str): Identifier used to locate out/{session_id}_coverage.csv, out/{session_id}_notes.md, and out/{session_id}_citations.json.
    
    Returns:
        dict: Report with keys:
            - session_id: the provided session identifier.
            - coverage: list of coverage records (each a dict) loaded from CSV, or empty list.
            - qa: summary dict with keys `formulas_checked`, `links_verified`, `citations_found`, and `warnings` when QA notes are present, otherwise empty dict.
            - citations: list loaded from citations JSON, or empty list.
            - coverage_path: string path to the coverage CSV when present, otherwise None.
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
    Write a human-readable text summary of a report to the given file path.
    
    Parameters:
        report (Dict[str, Any]): Report dictionary produced by `generate_report`. Expected keys used:
            - session_id (str): Identifier included in the header.
            - coverage (List[Dict]): Optional; each item should contain `name` (str),
              `coverage_percentage` (float), and `chunk_count` (int).
            - qa (Dict): Optional; may contain `formulas_checked`, `links_verified`,
              `citations_found`, and `warnings` (all ints).
            - citations (List): Optional; list of citation entries.
        output_path (Path): Filesystem path where the composed text will be written.
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
    Write the report dictionary to a JSON file at the specified output path.
    
    Parameters:
        report (Dict[str, Any]): The report content to serialize.
        output_path (Path): Filesystem path where the JSON file will be written.
    """
    from examkit.utils.io_utils import write_json
    write_json(report, output_path)