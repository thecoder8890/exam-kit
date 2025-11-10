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
    Transcribe audio file using faster-whisper.

    Args:
        audio_path: Path to audio file (WAV recommended).
        model_size: Whisper model size (tiny, base, small, medium, large).
        language: Language code (en, es, fr, etc.).
        vad: Enable Voice Activity Detection.
        logger: Logger instance.

    Returns:
        List of transcription segments.
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
    Transcribe audio with detailed timestamp information.

    Args:
        audio_path: Path to audio file.
        model_size: Whisper model size.
        language: Language code.
        logger: Logger instance.

    Returns:
        Dictionary with transcription and metadata.
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
    Export transcription segments to VTT format.

    Args:
        segments: List of transcription segments.
        output_path: Path for output VTT file.
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
