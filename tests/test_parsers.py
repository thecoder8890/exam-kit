"""
Tests for parsing modules.
"""

import pytest

from examkit.ingestion.exam_parser import extract_marks, parse_exam_structure


def test_extract_marks():
    """Test marks extraction."""
    assert extract_marks("[5 marks]") == 5
    assert extract_marks("(10 marks)") == 10
    assert extract_marks("[15]") == 15
    assert extract_marks("No marks here") == 0


def test_parse_exam_structure():
    """Test exam structure parsing."""
    exam_text = """
Section A

Question 1. [10 marks]
Define a matrix.

a) What is a determinant? [5 marks]
b) Calculate the following. [5 marks]

Question 2. [15 marks]
Explain calculus.
"""
    questions = parse_exam_structure(exam_text)
    assert len(questions) >= 1
    assert questions[0]["section"] == "A"
    assert questions[0]["question_number"] == 1


def test_timecode_conversion():
    """Test timecode utilities."""
    from examkit.utils.timecode import seconds_to_timecode, timecode_to_seconds

    assert seconds_to_timecode(125) == "00:02:05"
    assert timecode_to_seconds("00:02:05") == 125.0
    assert timecode_to_seconds("02:05") == 125.0


def test_text_cleaning():
    """Test text utilities."""
    from examkit.utils.text_utils import clean_text, normalize_whitespace

    dirty_text = "  Hello   world  \n\n  "
    assert clean_text(dirty_text) == "Hello world"
    assert normalize_whitespace(dirty_text) == "Hello world"


def test_math_utils():
    """Test math utilities."""
    from examkit.utils.math_utils import extract_latex_formulas, validate_latex_formula

    text = "The formula is $E = mc^2$ and $$\\int_0^1 x dx = \\frac{1}{2}$$"
    formulas = extract_latex_formulas(text)
    assert len(formulas) == 2

    assert validate_latex_formula("x^2 + y^2 = z^2")
    assert not validate_latex_formula("\\frac{1}{2")  # Unclosed brace
