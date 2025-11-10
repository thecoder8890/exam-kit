"""
Transcript normalization from VTT/SRT/TXT to JSONL format.
"""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List

from examkit.utils.timecode import parse_vtt_timestamp


def parse_vtt(content: str) -> List[Dict[str, Any]]:
    """
    Parse VTT (WebVTT) transcript format.

    Args:
        content: VTT file content.

    Returns:
        List of segment dictionaries.
    """
    segments = []
    lines = content.split('\n')

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Look for timestamp line (contains -->)
        if '-->' in line:
            # Parse timestamps
            timestamp_match = re.match(r'([\d:\.]+)\s*-->\s*([\d:\.]+)', line)
            if timestamp_match:
                start_str, end_str = timestamp_match.groups()
                start = parse_vtt_timestamp(start_str)
                end = parse_vtt_timestamp(end_str)

                # Collect text lines until empty line
                text_lines = []
                i += 1
                while i < len(lines) and lines[i].strip():
                    text_lines.append(lines[i].strip())
                    i += 1

                text = ' '.join(text_lines)
                if text:
                    segments.append({
                        "source": "transcript",
                        "type": "vtt",
                        "start": start,
                        "end": end,
                        "text": text
                    })

        i += 1

    return segments


def parse_srt(content: str) -> List[Dict[str, Any]]:
    """
    Parse SRT (SubRip) transcript format.

    Args:
        content: SRT file content.

    Returns:
        List of segment dictionaries.
    """
    segments = []
    blocks = content.strip().split('\n\n')

    for block in blocks:
        lines = block.split('\n')
        if len(lines) < 3:
            continue

        # Second line should have timestamps
        timestamp_line = lines[1]
        timestamp_match = re.match(r'([\d:,]+)\s*-->\s*([\d:,]+)', timestamp_line)

        if timestamp_match:
            start_str, end_str = timestamp_match.groups()
            # Convert comma to dot for milliseconds
            start_str = start_str.replace(',', '.')
            end_str = end_str.replace(',', '.')

            start = parse_vtt_timestamp(start_str)
            end = parse_vtt_timestamp(end_str)

            # Remaining lines are text
            text = ' '.join(lines[2:])
            if text:
                segments.append({
                    "source": "transcript",
                    "type": "srt",
                    "start": start,
                    "end": end,
                    "text": text
                })

    return segments


def parse_txt(content: str) -> List[Dict[str, Any]]:
    """
    Parse plain text transcript (no timestamps).

    Args:
        content: Plain text content.

    Returns:
        List of segment dictionaries (with dummy timestamps).
    """
    # Split into paragraphs
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

    segments = []
    for i, para in enumerate(paragraphs):
        segments.append({
            "source": "transcript",
            "type": "txt",
            "start": None,
            "end": None,
            "text": para,
            "index": i
        })

    return segments


def normalize_transcript(path: Path, logger: logging.Logger) -> List[Dict[str, Any]]:
    """
    Normalize transcript from various formats to standardized JSONL.

    Args:
        path: Path to transcript file.
        logger: Logger instance.

    Returns:
        List of normalized transcript segments.
    """
    logger.info(f"Normalizing transcript: {path}")

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    suffix = path.suffix.lower()

    if suffix == '.vtt':
        segments = parse_vtt(content)
    elif suffix == '.srt':
        segments = parse_srt(content)
    elif suffix == '.txt':
        segments = parse_txt(content)
    else:
        logger.warning(f"Unknown transcript format: {suffix}, treating as plain text")
        segments = parse_txt(content)

    # Sort by start time if available
    segments_with_time = [s for s in segments if s.get('start') is not None]
    segments_without_time = [s for s in segments if s.get('start') is None]

    segments_with_time.sort(key=lambda x: x['start'])

    logger.info(f"Normalized {len(segments)} segments from {suffix} format")
    return segments_with_time + segments_without_time
