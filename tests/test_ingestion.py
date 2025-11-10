"""
Tests for ingestion module.
"""

import pytest
from pathlib import Path

from examkit.ingestion.transcript_normalizer import parse_vtt, parse_srt, parse_txt


def test_parse_vtt():
    """Test VTT parsing."""
    vtt_content = """WEBVTT

1
00:00:00.000 --> 00:00:05.000
Hello world

2
00:00:05.000 --> 00:00:10.000
This is a test
"""
    segments = parse_vtt(vtt_content)
    assert len(segments) == 2
    assert segments[0]["text"] == "Hello world"
    assert segments[0]["start"] == 0.0
    assert segments[0]["end"] == 5.0


def test_parse_srt():
    """Test SRT parsing."""
    srt_content = """1
00:00:00,000 --> 00:00:05,000
Hello world

2
00:00:05,000 --> 00:00:10,000
This is a test
"""
    segments = parse_srt(srt_content)
    assert len(segments) == 2
    assert segments[0]["text"] == "Hello world"
    assert segments[0]["start"] == 0.0


def test_parse_txt():
    """Test plain text parsing."""
    txt_content = """First paragraph.

Second paragraph.

Third paragraph."""
    segments = parse_txt(txt_content)
    assert len(segments) == 3
    assert segments[0]["text"] == "First paragraph."


def test_validate_manifest():
    """Test manifest validation."""
    from examkit.ingestion.ingest import validate_manifest

    valid_manifest = {
        "session_id": "test",
        "inputs": {
            "video": "test.mp4"
        }
    }
    assert validate_manifest(valid_manifest) is True

    with pytest.raises(ValueError):
        validate_manifest({})

    with pytest.raises(ValueError):
        validate_manifest({"session_id": "test"})
