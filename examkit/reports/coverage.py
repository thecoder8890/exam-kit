"""
Topic coverage reporting.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd


def generate_coverage_report(
    coverage_data: List[Dict[str, Any]],
    output_path: Path,
    logger: logging.Logger = None
) -> pd.DataFrame:
    """
    Generate topic coverage report.

    Args:
        coverage_data: List of coverage dictionaries.
        output_path: Path to save CSV report.
        logger: Logger instance.

    Returns:
        DataFrame with coverage data.
    """
    df = pd.DataFrame(coverage_data)

    # Sort by coverage percentage
    if "coverage_percentage" in df.columns:
        df = df.sort_values("coverage_percentage", ascending=False)

    # Save to CSV
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    if logger:
        logger.info(f"Coverage report saved to: {output_path}")

    return df


def calculate_overall_coverage(coverage_data: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Calculate overall coverage statistics.

    Args:
        coverage_data: List of coverage dictionaries.

    Returns:
        Dictionary with overall statistics.
    """
    if not coverage_data:
        return {"mean": 0.0, "median": 0.0, "min": 0.0, "max": 0.0}

    coverages = [item["coverage_percentage"] for item in coverage_data]

    stats = {
        "mean": sum(coverages) / len(coverages),
        "median": sorted(coverages)[len(coverages) // 2],
        "min": min(coverages),
        "max": max(coverages)
    }

    return stats


def identify_coverage_gaps(
    coverage_data: List[Dict[str, Any]],
    threshold: float = 10.0
) -> List[Dict[str, Any]]:
    """
    Identify topics with insufficient coverage.

    Args:
        coverage_data: List of coverage dictionaries.
        threshold: Minimum acceptable coverage percentage.

    Returns:
        List of under-covered topics.
    """
    gaps = []
    for item in coverage_data:
        if item["coverage_percentage"] < threshold:
            gaps.append(item)

    return gaps


def generate_coverage_summary(coverage_data: List[Dict[str, Any]]) -> str:
    """
    Generate a text summary of coverage.

    Args:
        coverage_data: List of coverage dictionaries.

    Returns:
        Text summary.
    """
    if not coverage_data:
        return "No coverage data available."

    stats = calculate_overall_coverage(coverage_data)
    gaps = identify_coverage_gaps(coverage_data)

    lines = [
        "Topic Coverage Summary",
        "=" * 50,
        f"Total Topics: {len(coverage_data)}",
        f"Mean Coverage: {stats['mean']:.1f}%",
        f"Median Coverage: {stats['median']:.1f}%",
        f"Coverage Range: {stats['min']:.1f}% - {stats['max']:.1f}%",
        ""
    ]

    if gaps:
        lines.append(f"⚠️ {len(gaps)} topics with low coverage (<10%):")
        for gap in gaps:
            lines.append(f"  - {gap['name']}: {gap['coverage_percentage']:.1f}%")
    else:
        lines.append("✓ All topics have adequate coverage")

    return "\n".join(lines)
