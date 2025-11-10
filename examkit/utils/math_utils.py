"""
Mathematical utilities.
"""

import re
from typing import List, Optional


def extract_latex_formulas(text: str) -> List[str]:
    """
    Extract LaTeX formulas from the given text, returning them without surrounding dollar delimiters.
    
    Parameters:
        text (str): Text that may contain LaTeX inline ($...$) or display ($$...$$) formulas.
    
    Returns:
        List[str]: A list of formula strings found (inline and display), with the surrounding `$`/`$$` removed.
    """
    # Match inline math: $...$
    inline = re.findall(r'\$([^\$]+)\$', text)
    # Match display math: $$...$$
    display = re.findall(r'\$\$([^\$]+)\$\$', text)
    return inline + display


def validate_latex_formula(formula: str) -> bool:
    """
    Validate basic structural correctness of a LaTeX formula string.
    
    Performs lightweight checks for balanced braces, brackets, and parentheses, and rejects common invalid patterns such as unclosed command arguments and literal double dollar signs.
    
    Parameters:
        formula (str): LaTeX formula string to validate.
    
    Returns:
        `True` if no issues are detected, `False` otherwise.
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
    Format a number to a fixed number of decimal places.
    
    Parameters:
        num (float): Value to format.
        precision (int): Number of digits after the decimal point.
    
    Returns:
        str: The formatted number as a string with exactly `precision` decimal places.
    """
    return f"{num:.{precision}f}"


def calculate_coverage_percentage(covered: int, total: int) -> float:
    """
    Compute the percentage of covered items out of a total.
    
    Parameters:
        covered (int): Number of covered items.
        total (int): Total number of items.
    
    Returns:
        float: Coverage percentage between 0 and 100. Returns 0.0 when `total` is 0.
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
    
    Parameters:
        formula (str): The LaTeX input string to scan for symbols.
    
    Returns:
        List[str]: Unique symbols found — single-letter alphabetic identifiers (a–z, A–Z) and common Greek letter names (e.g. "alpha", "beta") without the leading backslash.
    """
    # Simple extraction of single-letter variables
    symbols = re.findall(r'\b([a-zA-Z])\b', formula)
    # Also find Greek letters
    greek = re.findall(r'\\(alpha|beta|gamma|delta|epsilon|theta|lambda|mu|pi|sigma|tau|phi|psi|omega)', formula)
    return list(set(symbols + greek))


def is_numeric(value: str) -> bool:
    """
    Check if a string represents a numeric value.
    
    Returns:
        True if the string can be parsed as a float, False otherwise.
    """
    try:
        float(value)
        return True
    except ValueError:
        return False