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
    Create a topic coverage report from coverage_data and write it to output_path as a CSV.
    
    The function constructs a DataFrame from coverage_data, sorts it in descending order by the
    "coverage_percentage" column if present, ensures the parent directory of output_path exists,
    and writes the DataFrame to CSV without an index. If a logger is provided, an info message
    is emitted with the saved path.
    
    Parameters:
        coverage_data: Iterable of dictionaries describing topics; if a dictionary contains a
            "coverage_percentage" key it will be used for sorting. Each item typically includes
            a topic identifier (e.g., "name") and its coverage percentage.
        output_path: Filesystem path where the CSV report will be written.
    
    Returns:
        pd.DataFrame: The DataFrame created (and possibly sorted) from coverage_data.
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
    Compute summary statistics (mean, median, minimum, and maximum) for topic coverage percentages.
    
    Parameters:
        coverage_data (List[Dict[str, Any]]): Sequence of records where each record contains a `coverage_percentage` numeric value.
    
    Returns:
        Dict[str, float]: Dictionary with keys `"mean"`, `"median"`, `"min"`, and `"max"` mapping to their respective coverage values. If `coverage_data` is empty, all values are `0.0`.
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
    Produce a human-readable summary of topic coverage statistics and low-coverage topics.
    
    Parameters:
        coverage_data (List[Dict[str, Any]]): List of topic coverage records. Each record should include a
            `coverage_percentage` numeric value and a `name` string used when listing gaps.
    
    Returns:
        summary (str): Multi-line text containing total topics, mean, median, min/max coverage, and a
            list of topics with coverage below 10% (if any). If `coverage_data` is empty, returns
            "No coverage data available.".
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