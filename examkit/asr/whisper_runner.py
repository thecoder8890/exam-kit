"""
Faster-whisper wrapper for offline ASR.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List

try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False


def transcribe_audio(
    audio_path: Path,
    model_size: str = "small",
    language: str = "en",
    vad: bool = True,
    logger: logging.Logger = None
) -> List[Dict[str, Any]]:
    """
    Transcribe an audio file into timestamped segments using faster-whisper.
    
    Transcribes the given audio file with the specified Whisper model and returns a list of segment dictionaries containing start/end timestamps and cleaned text.
    
    Parameters:
        audio_path (Path): Path to the audio file.
        model_size (str): Whisper model size to load (e.g., "tiny", "base", "small", "medium", "large").
        language (str): Language code hint for transcription (e.g., "en", "es", "fr").
        vad (bool): Whether to enable voice activity detection to filter non-speech.
        logger (logging.Logger | None): Optional logger for informational messages.
    
    Returns:
        List[Dict[str, Any]]: A list of segments where each segment dictionary contains:
            - "source": "asr"
            - "type": "whisper"
            - "start": start time in seconds
            - "end": end time in seconds
            - "text": transcribed text (stripped of surrounding whitespace)
    
    Raises:
        ImportError: If faster-whisper is not available.
    """
    if not WHISPER_AVAILABLE:
        raise ImportError("faster-whisper not available. Install with: pip install faster-whisper")

    if logger:
        logger.info(f"Transcribing {audio_path} with model={model_size}, language={language}")

    # Load model
    model = WhisperModel(model_size, device="cpu", compute_type="int8")

    # Transcribe
    segments, info = model.transcribe(
        str(audio_path),
        language=language,
        vad_filter=vad,
        beam_size=5
    )

    # Convert to list
    transcription = []
    for segment in segments:
        transcription.append({
            "source": "asr",
            "type": "whisper",
            "start": segment.start,
            "end": segment.end,
            "text": segment.text.strip()
        })

    if logger:
        logger.info(f"Transcription complete: {len(transcription)} segments")
        logger.info(f"Detected language: {info.language} (probability: {info.language_probability:.2f})")

    return transcription


def transcribe_with_timestamps(
    audio_path: Path,
    model_size: str = "small",
    language: str = "en",
    logger: logging.Logger = None
) -> Dict[str, Any]:
    """
    Transcribe an audio file and return timestamped segments and summary metadata.
    
    Parameters:
        audio_path (Path): Path to the input audio file.
        model_size (str): Whisper model size identifier (e.g., "small").
        language (str): ISO language code to use for transcription.
    
    Returns:
        result (dict): Dictionary containing:
            - audio_file (str): String path of the input audio file.
            - model (str): Model size used.
            - language (str): Language code used.
            - segments (List[dict]): List of segment dictionaries each with keys `source`, `type`, `start`, `end`, and `text`.
            - total_duration (float): End time of the last segment in seconds, or 0.0 if no segments.
            - total_segments (int): Number of segments.
    """
    segments = transcribe_audio(audio_path, model_size, language, True, logger)

    result = {
        "audio_file": str(audio_path),
        "model": model_size,
        "language": language,
        "segments": segments,
        "total_duration": segments[-1]["end"] if segments else 0.0,
        "total_segments": len(segments)
    }

    return result


def export_to_vtt(segments: List[Dict[str, Any]], output_path: Path) -> None:
    """
    Write transcription segments to a WebVTT file at the given path.
    
    Each segment must be a mapping containing keys "start" (seconds, number), "end" (seconds, number)
    and "text" (string). The function creates or overwrites the file at output_path and writes
    a valid WEBVTT document where each segment is numbered and formatted as a time range with text.
    Parameters:
        segments (List[Dict[str, Any]]): Ordered transcription segments with "start", "end", and "text".
        output_path (Path): Filesystem path to write the .vtt file; existing file will be overwritten.
    """
    from examkit.utils.timecode import seconds_to_timecode

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("WEBVTT\n\n")

        for i, segment in enumerate(segments, start=1):
            start = seconds_to_timecode(segment["start"])
            end = seconds_to_timecode(segment["end"])
            text = segment["text"]

            f.write(f"{i}\n")
            f.write(f"{start} --> {end}\n")
            f.write(f"{text}\n\n")