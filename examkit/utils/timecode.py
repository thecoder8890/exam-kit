"""
Timecode utilities for video timestamps.
"""

from typing import Tuple


def seconds_to_timecode(seconds: float) -> str:
    """
    Convert seconds to HH:MM:SS timecode format.

    Args:
        seconds: Time in seconds.

    Returns:
        Formatted timecode string (HH:MM:SS).
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def timecode_to_seconds(timecode: str) -> float:
    """
    Convert HH:MM:SS timecode to seconds.

    Args:
        timecode: Timecode string (HH:MM:SS or MM:SS).

    Returns:
        Time in seconds.
    """
    parts = timecode.split(':')
    if len(parts) == 3:
        hours, minutes, seconds = parts
        return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    elif len(parts) == 2:
        minutes, seconds = parts
        return int(minutes) * 60 + float(seconds)
    else:
        return float(parts[0])


def format_duration(seconds: float) -> str:
    """
    Format duration in a human-readable way.

    Args:
        seconds: Duration in seconds.

    Returns:
        Formatted duration string.
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def parse_vtt_timestamp(timestamp: str) -> float:
    """
    Parse VTT timestamp format to seconds.

    Args:
        timestamp: VTT timestamp (e.g., "00:01:23.456").

    Returns:
        Time in seconds.
    """
    # Remove milliseconds if present
    if '.' in timestamp:
        timestamp, _ = timestamp.split('.')

    return timecode_to_seconds(timestamp)


def create_video_citation(timecode: str, description: str = "") -> str:
    """
    Create a formatted video citation.

    Args:
        timecode: Video timecode.
        description: Optional description.

    Returns:
        Formatted citation string.
    """
    if description:
        return f"[vid {timecode}] {description}"
    return f"[vid {timecode}]"


def extract_time_range(start: float, end: float) -> Tuple[str, str]:
    """
    Extract time range as formatted timecodes.

    Args:
        start: Start time in seconds.
        end: End time in seconds.

    Returns:
        Tuple of (start_timecode, end_timecode).
    """
    return seconds_to_timecode(start), seconds_to_timecode(end)
