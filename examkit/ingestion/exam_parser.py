"""
Exam paper parser for extracting questions and structure.
"""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List

import fitz  # PyMuPDF


def extract_marks(text: str) -> int:
    """
    Extract marks from text using common patterns.

    Args:
        text: Text containing marks information.

    Returns:
        Number of marks (0 if not found).
    """
    # Common patterns: [5 marks], (5 marks), [5], (5)
    patterns = [
        r'\[(\d+)\s*marks?\]',
        r'\((\d+)\s*marks?\)',
        r'\[(\d+)\]',
        r'\((\d+)\)',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1))

    return 0


def parse_exam_structure(text: str) -> List[Dict[str, Any]]:
    """
    Parse exam structure from text.

    Args:
        text: Exam paper text content.

    Returns:
        List of question dictionaries.
    """
    questions = []
    lines = text.split('\n')

    current_section = None
    current_question = None
    current_part = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check for section headers (Section A, Section B, etc.)
        section_match = re.match(r'Section\s+([A-Z])', line, re.IGNORECASE)
        if section_match:
            current_section = section_match.group(1)
            continue

        # Check for question numbers (Question 1, Q1, 1., etc.)
        question_match = re.match(r'(?:Question\s+)?(\d+)[.)]', line, re.IGNORECASE)
        if question_match:
            if current_question:
                questions.append(current_question)

            question_num = question_match.group(1)
            current_question = {
                "source": "exam",
                "section": current_section,
                "question_id": f"Q{question_num}",
                "question_number": int(question_num),
                "text": line,
                "parts": [],
                "marks": extract_marks(line)
            }
            current_part = None
            continue

        # Check for question parts (a), b), (i), etc.)
        part_match = re.match(r'[\(\[]?([a-z]|[ivxIVX]+)[\)\]]', line)
        if part_match and current_question:
            if current_part:
                current_question["parts"].append(current_part)

            part_id = part_match.group(1)
            current_part = {
                "part_id": part_id,
                "text": line,
                "marks": extract_marks(line)
            }
            continue

        # Add to current question or part
        if current_part:
            current_part["text"] += " " + line
        elif current_question:
            current_question["text"] += " " + line

    # Add last question and part
    if current_part and current_question:
        current_question["parts"].append(current_part)
    if current_question:
        questions.append(current_question)

    return questions


def parse_exam(path: Path, logger: logging.Logger) -> List[Dict[str, Any]]:
    """
    Parse exam paper PDF.

    Args:
        path: Path to exam PDF file.
        logger: Logger instance.

    Returns:
        List of question dictionaries.
    """
    logger.info(f"Parsing exam paper: {path}")

    doc = fitz.open(str(path))
    full_text = ""

    # Extract all text from PDF
    for page in doc:
        full_text += page.get_text() + "\n"

    doc.close()

    # Parse structure
    questions = parse_exam_structure(full_text)

    logger.info(f"Parsed {len(questions)} questions from exam paper")
    return questions
