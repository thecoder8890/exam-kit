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
    Convert a timecode string into total seconds.
    
    Accepts 'HH:MM:SS', 'MM:SS', or a single numeric string; the seconds component may include a fractional part.
    
    Parameters:
        timecode (str): Timecode in one of the accepted formats.
    
    Returns:
        float: Total seconds represented by the timecode.
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
    Format a duration (in seconds) into a concise human-readable string.
    
    The function discards any fractional part of the input seconds and emits:
    - "Xh Ym Zs" when hours > 0
    - "Ym Zs" when hours == 0 and minutes > 0
    - "Zs" when only seconds remain
    
    Parameters:
        seconds (float): Duration in seconds; fractional seconds are discarded.
    
    Returns:
        str: Formatted duration string (e.g., "1h 2m 3s", "5m 30s", "45s").
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
    Parse a WebVTT timestamp into total seconds.
    
    Fractional seconds (milliseconds) are ignored; the timestamp may be in "HH:MM:SS.ms" or "MM:SS.ms" form.
    
    Parameters:
        timestamp (str): VTT timestamp string, e.g. "00:01:23.456" or "01:23.456".
    
    Returns:
        float: Total seconds represented by the timestamp.
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
    Return start and end times formatted as HH:MM:SS timecodes.
    
    Parameters:
        start (float): Start time in seconds.
        end (float): End time in seconds.
    
    Returns:
        tuple[str, str]: A tuple (start_timecode, end_timecode) where each element is the corresponding time formatted as "HH:MM:SS".
    """
    return seconds_to_timecode(start), seconds_to_timecode(end)