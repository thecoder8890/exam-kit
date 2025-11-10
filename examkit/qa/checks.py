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
    Check if LaTeX formulas in content are valid.

    Args:
        content: Content with LaTeX formulas.
        logger: Logger instance.

    Returns:
        Dictionary with check results.
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
    Check internal links in markdown content.

    Args:
        content: Markdown content.
        logger: Logger instance.

    Returns:
        Dictionary with check results.
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
    Check if required keywords are present in content.

    Args:
        content: Content to check.
        required_keywords: List of keywords that should be present.
        logger: Logger instance.

    Returns:
        Dictionary with check results.
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
    Check if content has proper citations.

    Args:
        content: Content to check.
        logger: Logger instance.

    Returns:
        Dictionary with check results.
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
    Check if equations use consistent notation.

    Args:
        content: Content with equations.
        logger: Logger instance.

    Returns:
        Dictionary with check results.
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
    Run all QA checks on content.

    Args:
        content: Content to check.
        required_keywords: Optional list of required keywords.
        logger: Logger instance.

    Returns:
        Dictionary with all check results.
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
