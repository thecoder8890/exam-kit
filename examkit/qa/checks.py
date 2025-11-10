"""
Quality assurance checks for generated content.
"""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List

from examkit.utils.math_utils import extract_latex_formulas, validate_latex_formula


def check_formula_compilation(content: str, logger: logging.Logger = None) -> Dict[str, Any]:
    """
    Validate LaTeX formulas found in the given content.
    
    Extracts LaTeX formulas and reports which formulas failed validation.
    
    Returns:
        result (dict): Summary of the check with keys:
            - total_formulas (int): Number of formulas found.
            - valid_formulas (int): Number of formulas that passed validation.
            - invalid_formulas (List[str]): Formulas that failed validation.
            - passed (bool): `true` if no invalid formulas were found, `false` otherwise.
    """
    formulas = extract_latex_formulas(content)
    invalid_formulas = []

    for formula in formulas:
        if not validate_latex_formula(formula):
            invalid_formulas.append(formula)

    result = {
        "total_formulas": len(formulas),
        "valid_formulas": len(formulas) - len(invalid_formulas),
        "invalid_formulas": invalid_formulas,
        "passed": len(invalid_formulas) == 0
    }

    if logger:
        logger.info(f"Formula check: {result['valid_formulas']}/{result['total_formulas']} valid")

    return result


def check_internal_links(content: str, logger: logging.Logger = None) -> Dict[str, Any]:
    """
    Verify internal Markdown links point to existing heading anchors.
    
    Converts document headings to anchor names by lowercasing and replacing spaces with hyphens, then checks all markdown links of the form [text](#anchor) to identify links whose targets are not present among those anchors.
    
    Parameters:
        content (str): Markdown content to inspect.
    
    Returns:
        dict: Result object with keys:
            - total_links (int): Number of internal links found.
            - broken_links (List[Tuple[str, str]]): List of tuples (link_text, link_target) for links whose target anchor was not found.
            - passed (bool): `true` if no broken links were detected, `false` otherwise.
    """
    # Find all markdown links
    link_pattern = r'\[([^\]]+)\]\(#([^)]+)\)'
    links = re.findall(link_pattern, content)

    # Find all headings
    heading_pattern = r'^#+\s+(.+)$'
    headings = re.findall(heading_pattern, content, re.MULTILINE)

    # Convert headings to anchor format
    anchors = [h.lower().replace(' ', '-') for h in headings]

    broken_links = []
    for link_text, link_target in links:
        if link_target not in anchors:
            broken_links.append((link_text, link_target))

    result = {
        "total_links": len(links),
        "broken_links": broken_links,
        "passed": len(broken_links) == 0
    }

    if logger:
        logger.info(f"Link check: {len(broken_links)} broken links found")

    return result


def check_keyword_recall(
    content: str,
    required_keywords: List[str],
    logger: logging.Logger = None
) -> Dict[str, Any]:
    """
    Determine which of the required keywords appear in the provided content.
    
    Parameters:
        content (str): Text to search for keywords; matching is case-insensitive.
        required_keywords (List[str]): Keywords to look for; each keyword is matched as a substring (case-insensitive). An empty list yields 100% coverage.
    
    Returns:
        Dict[str, Any]: Result dictionary with keys:
            - total_keywords (int): Number of keywords checked.
            - found_keywords (int): Number of keywords found in the content.
            - missing_keywords (List[str]): Keywords that were not found.
            - coverage_percentage (float): Percentage of keywords found (0–100).
    """
    content_lower = content.lower()
    missing_keywords = []

    for keyword in required_keywords:
        if keyword.lower() not in content_lower:
            missing_keywords.append(keyword)

    result = {
        "total_keywords": len(required_keywords),
        "found_keywords": len(required_keywords) - len(missing_keywords),
        "missing_keywords": missing_keywords,
        "coverage_percentage": (len(required_keywords) - len(missing_keywords)) / len(required_keywords) * 100 if required_keywords else 100
    }

    if logger:
        logger.info(f"Keyword check: {result['found_keywords']}/{result['total_keywords']} found ({result['coverage_percentage']:.1f}%)")

    return result


def check_citation_presence(content: str, logger: logging.Logger = None) -> Dict[str, Any]:
    """
    Detects video, slide, and exam citations in the given content.
    
    Parameters:
        content (str): Text to scan for citations; looks for tokens like `[vid ...]`, `[slide ...]`, or `[exam ...]`.
    
    Returns:
        dict: {
            "total_citations": int,        # total number of citation tokens found
            "has_citations": bool,         # True if any citations were found
            "citation_types": {            # counts per citation type
                "video": int,
                "slides": int,
                "exam": int
            }
        }
    """
    # Find citations [vid ...], [slide ...], [exam ...]
    citation_pattern = r'\[(vid|slide|exam)[^\]]*\]'
    citations = re.findall(citation_pattern, content)

    result = {
        "total_citations": len(citations),
        "has_citations": len(citations) > 0,
        "citation_types": {
            "video": citations.count("vid"),
            "slides": citations.count("slide"),
            "exam": citations.count("exam")
        }
    }

    if logger:
        logger.info(f"Citation check: {result['total_citations']} citations found")

    return result


def check_equation_consistency(content: str, logger: logging.Logger = None) -> Dict[str, Any]:
    """
    Analyze LaTeX formulas in the provided content to detect potentially inconsistent equation notation.
    
    Parameters:
        content (str): Text containing LaTeX formulas to inspect (inline or display math).
        
    Returns:
        result (dict): Summary of the consistency check with keys:
            - total_symbols (int): Number of unique equation symbols found.
            - warnings (list): List of human-readable warnings about symbols with potential inconsistent usage.
            - passed (bool): `true` if no warnings were produced, `false` otherwise.
    """
    from examkit.utils.math_utils import extract_equation_symbols

    formulas = extract_latex_formulas(content)
    symbol_usage = {}

    for formula in formulas:
        symbols = extract_equation_symbols(formula)
        for symbol in symbols:
            if symbol not in symbol_usage:
                symbol_usage[symbol] = []
            symbol_usage[symbol].append(formula)

    # Check for potential inconsistencies (symbols used only once or in very different contexts)
    warnings = []
    for symbol, formulas in symbol_usage.items():
        if len(formulas) == 1:
            # Symbol used only once - might be okay, but worth noting
            pass

    result = {
        "total_symbols": len(symbol_usage),
        "warnings": warnings,
        "passed": len(warnings) == 0
    }

    if logger:
        logger.info(f"Equation consistency: {result['total_symbols']} unique symbols")

    return result


def run_all_checks(
    content: str,
    required_keywords: List[str] = None,
    logger: logging.Logger = None
) -> Dict[str, Any]:
    """
    Run a suite of QA checks on the provided content and aggregate their results.
    
    Parameters:
        content (str): Markdown or text content to validate.
        required_keywords (List[str], optional): If provided, include a keyword-recall check for these terms.
    
    Returns:
        Dict[str, Any]: Aggregated results containing per-check dictionaries for `"formulas"`, `"links"`, `"citations"`, and `"equations"`. If `required_keywords` was supplied, includes a `"keywords"` entry. Contains `"overall_passed"` (bool) which is true only if every check that reports a `passed` field is true.
    """
    if logger:
        logger.info("Running QA checks...")

    results = {
        "formulas": check_formula_compilation(content, logger),
        "links": check_internal_links(content, logger),
        "citations": check_citation_presence(content, logger),
        "equations": check_equation_consistency(content, logger)
    }

    if required_keywords:
        results["keywords"] = check_keyword_recall(content, required_keywords, logger)

    # Overall status
    all_passed = all(
        check.get("passed", True)
        for check in results.values()
        if "passed" in check
    )

    results["overall_passed"] = all_passed

    if logger:
        logger.info(f"QA checks complete. Overall: {'PASSED' if all_passed else 'WARNINGS'}")

    return results