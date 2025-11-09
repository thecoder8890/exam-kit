"""
Tests for topic mapping and NLP modules.
"""

import pytest
import numpy as np

from examkit.nlp.topic_mapping import load_topics, calculate_coverage
from examkit.nlp.splitter import split_into_chunks, merge_short_segments


def test_load_topics():
    """Test topic loading."""
    topics_data = [
        {"id": "topic1", "name": "Topic 1", "keywords": ["key1"], "weight": 1.0},
        {"name": "Topic 2", "keywords": ["key2"]}
    ]
    topics = load_topics(topics_data)
    assert len(topics) == 2
    assert topics[0]["id"] == "topic1"
    assert topics[1]["id"] == "topic_2"  # Auto-generated


def test_calculate_coverage():
    """Test coverage calculation."""
    topic_mapping = {
        "topic1": [0, 1, 2],
        "topic2": [3, 4]
    }
    topics = [
        {"id": "topic1", "name": "Topic 1", "weight": 1.0},
        {"id": "topic2", "name": "Topic 2", "weight": 1.0}
    ]
    coverage = calculate_coverage(topic_mapping, topics, total_chunks=10)
    assert len(coverage) == 2
    assert coverage[0]["chunk_count"] == 3
    assert coverage[0]["coverage_percentage"] == 30.0


def test_split_into_chunks():
    """Test chunk splitting."""
    segments = [
        {"text": "Short text", "source": "test"},
        {"text": "This is a very long text that should be split into multiple chunks because it exceeds the maximum chunk size and needs to be processed in smaller pieces for better handling", "source": "test"}
    ]
    chunks = split_into_chunks(segments, max_chunk_size=50)
    assert len(chunks) > 2  # Second segment should be split


def test_merge_short_segments():
    """Test merging short segments."""
    segments = [
        {"text": "A", "source": "test"},
        {"text": "B", "source": "test"},
        {"text": "This is a longer segment that should not be merged", "source": "test"}
    ]
    merged = merge_short_segments(segments, min_length=30)
    assert len(merged) < len(segments)


def test_citation_manager():
    """Test citation manager."""
    from examkit.synthesis.citations import CitationManager

    mgr = CitationManager()
    cite_id = mgr.add_citation("video", "v1", "Some content")
    assert cite_id is not None
    assert mgr.get_citation_count() == 1

    chunk = {"source": "transcript", "start": 125.5}
    citation = mgr.format_citation(chunk)
    assert "vid" in citation
    assert "02:05" in citation


def test_qa_checks():
    """Test QA checks."""
    from examkit.qa.checks import check_formula_compilation, check_citation_presence

    content = "The formula $E = mc^2$ is famous. [vid 00:01:23]"
    formula_result = check_formula_compilation(content)
    assert formula_result["total_formulas"] == 1

    citation_result = check_citation_presence(content)
    assert citation_result["has_citations"] is True
    assert citation_result["citation_types"]["video"] == 1
