"""
Mathematical utilities.
"""

import re
from typing import List, Optional


def extract_latex_formulas(text: str) -> List[str]:
    """
    Extract LaTeX formulas from text.

    Args:
        text: Input text containing LaTeX formulas.

    Returns:
        List of extracted formulas.
    """
    # Match inline math: $...$
    inline = re.findall(r'\$([^\$]+)\$', text)
    # Match display math: $$...$$
    display = re.findall(r'\$\$([^\$]+)\$\$', text)
    return inline + display


def validate_latex_formula(formula: str) -> bool:
    """
    Basic validation of LaTeX formula syntax.

    Args:
        formula: LaTeX formula string.

    Returns:
        True if formula appears valid, False otherwise.
    """
    # Check for balanced braces
    if formula.count('{') != formula.count('}'):
        return False
    if formula.count('[') != formula.count(']'):
        return False
    if formula.count('(') != formula.count(')'):
        return False

    # Check for common LaTeX commands
    invalid_patterns = [
        r'\\[a-zA-Z]+\s*\{[^}]*$',  # Unclosed command
        r'\$\$',  # Double dollar signs
    ]

    for pattern in invalid_patterns:
        if re.search(pattern, formula):
            return False

    return True


def format_number(num: float, precision: int = 2) -> str:
    """
    Format a number with specified precision.

    Args:
        num: Number to format.
        precision: Decimal precision.

    Returns:
        Formatted number string.
    """
    return f"{num:.{precision}f}"


def calculate_coverage_percentage(covered: int, total: int) -> float:
    """
    Calculate coverage percentage.

    Args:
        covered: Number of covered items.
        total: Total number of items.

    Returns:
        Coverage percentage (0-100).
    """
    if total == 0:
        return 0.0
    return (covered / total) * 100


def normalize_score(score: float, min_val: float, max_val: float) -> float:
    """
    Normalize a score to 0-1 range.

    Args:
        score: Score to normalize.
        min_val: Minimum possible value.
        max_val: Maximum possible value.

    Returns:
        Normalized score (0-1).
    """
    if max_val == min_val:
        return 0.0
    return (score - min_val) / (max_val - min_val)


def extract_equation_symbols(formula: str) -> List[str]:
    """
    Extract variable symbols from a LaTeX formula.

    Args:
        formula: LaTeX formula.

    Returns:
        List of variable symbols found.
    """
    # Simple extraction of single-letter variables
    symbols = re.findall(r'\b([a-zA-Z])\b', formula)
    # Also find Greek letters
    greek = re.findall(r'\\(alpha|beta|gamma|delta|epsilon|theta|lambda|mu|pi|sigma|tau|phi|psi|omega)', formula)
    return list(set(symbols + greek))


def is_numeric(value: str) -> bool:
    """
    Check if a string represents a numeric value.

    Args:
        value: String to check.

    Returns:
        True if numeric, False otherwise.
    """
    try:
        float(value)
        return True
    except ValueError:
        return False
