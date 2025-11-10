"""
Tests for rendering modules.
"""

import pytest
from pathlib import Path

from examkit.render.templater import render_markdown_document
from examkit.config import ExamKitConfig


def test_render_markdown_document():
    """Test markdown document rendering."""
    sections = [
        {
            "topic": "Test Topic",
            "definition": "This is a test definition.",
            "citations": "[vid 00:01:00]"
        }
    ]
    config = ExamKitConfig()
    markdown = render_markdown_document(sections, "test_session", config)

    assert "Test Topic" in markdown
    assert "Definition" in markdown
    assert "This is a test definition" in markdown
    assert "[vid 00:01:00]" in markdown


def test_typst_wrapper_creation():
    """Test Typst wrapper creation."""
    from examkit.render.typst_renderer import create_typst_wrapper_for_markdown
    from examkit.utils.io_utils import write_text
    import tempfile

    md_content = """# Test Title

## Section 1

This is some content.

### Subsection

More content here.
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(md_content)
        temp_path = Path(f.name)

    try:
        typst_content = create_typst_wrapper_for_markdown(temp_path)
        assert "= Test Title" in typst_content
        assert "== Section 1" in typst_content
        assert "=== Subsection" in typst_content
    finally:
        temp_path.unlink()


def test_config_loading():
    """
    Verifies that ExamKitConfig.from_yaml correctly loads ASR, LLM, and offline settings from a YAML configuration.
    
    Creates a temporary YAML configuration containing `asr.model`, `llm.model`, and `offline`, loads it via `ExamKitConfig.from_yaml`, and asserts the resulting object's fields match the expected values.
    """
    import tempfile
    import yaml

    config_data = {
        "asr": {"model": "small"},
        "llm": {"model": "llama3.2:8b"},
        "offline": True
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
        yaml.dump(config_data, f)
        temp_path = Path(f.name)

    try:
        config = ExamKitConfig.from_yaml(temp_path)
        assert config.asr.model == "small"
        assert config.llm.model == "llama3.2:8b"
        assert config.offline is True
    finally:
        temp_path.unlink()


def test_jinja_template_setup():
    """Test Jinja2 template environment setup."""
    from examkit.render.templater import setup_jinja_environment

    env = setup_jinja_environment()
    assert env is not None


def test_coverage_report():
    """Test coverage report generation."""
    from examkit.reports.coverage import calculate_overall_coverage, generate_coverage_summary

    coverage_data = [
        {"name": "Topic 1", "coverage_percentage": 80.0, "chunk_count": 10},
        {"name": "Topic 2", "coverage_percentage": 5.0, "chunk_count": 1},
        {"name": "Topic 3", "coverage_percentage": 60.0, "chunk_count": 8}
    ]

    stats = calculate_overall_coverage(coverage_data)
    assert stats["mean"] == pytest.approx(48.33, rel=0.1)
    assert stats["min"] == 5.0
    assert stats["max"] == 80.0

    summary = generate_coverage_summary(coverage_data)
    assert "Total Topics: 3" in summary
    assert "low coverage" in summary