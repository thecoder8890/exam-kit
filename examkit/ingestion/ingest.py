"""
Main ingestion pipeline for processing input files.
"""

import logging
from pathlib import Path
from typing import Any, Dict

import ffmpeg
from tqdm import tqdm

from examkit.utils.io_utils import ensure_dir, write_json


def validate_manifest(manifest: Dict[str, Any]) -> bool:
    """
    Validate that a manifest contains required fields and that its 'inputs' value is a dictionary.
    
    Parameters:
        manifest (Dict[str, Any]): Manifest data expected to include at least the keys `"session_id"` and `"inputs"`.
    
    Returns:
        bool: `True` if the manifest contains the required keys and `'inputs'` is a dictionary.
    
    Raises:
        ValueError: If a required key is missing or if `manifest["inputs"]` is not a dictionary.
    """
    required_keys = ["session_id", "inputs"]
    for key in required_keys:
        if key not in manifest:
            raise ValueError(f"Missing required key in manifest: {key}")

    inputs = manifest["inputs"]
    if not isinstance(inputs, dict):
        raise ValueError("'inputs' must be a dictionary")

    return True


def extract_audio_from_video(video_path: Path, output_path: Path, logger: logging.Logger) -> Path:
    """
    Extract audio from a video file and save it as a 16 kHz mono PCM WAV.
    
    Parameters:
        video_path (Path): Path to the input video file.
        output_path (Path): Destination path for the extracted WAV file; the function will create the parent directory if needed.
    
    Returns:
        Path: Path to the extracted audio file.
    
    Raises:
        ffmpeg.Error: If FFmpeg fails during extraction.
    """
    logger.info(f"Extracting audio from {video_path}")

    try:
        ensure_dir(output_path.parent)

        # Extract audio as 16kHz mono WAV
        stream = ffmpeg.input(str(video_path))
        stream = ffmpeg.output(
            stream,
            str(output_path),
            acodec='pcm_s16le',
            ac=1,
            ar='16000'
        )
        ffmpeg.run(stream, overwrite_output=True, quiet=True)

        logger.info(f"Audio extracted to {output_path}")
        return output_path

    except ffmpeg.Error as e:
        logger.error(f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}")
        raise


def ingest_pipeline(
    manifest: Dict[str, Any],
    cache_dir: Path,
    logger: logging.Logger
) -> Dict[str, Any]:
    """
    Run the ingestion pipeline for a session and produce processed outputs in the cache directory.
    
    Parameters:
        manifest (Dict[str, Any]): Manifest containing at least "session_id" and an "inputs" mapping of optional keys: "video", "transcript", "slides", "exam".
        cache_dir (Path): Directory where processed files and the normalized manifest will be written.
        logger (logging.Logger): Logger used for informational and warning messages.
    
    Returns:
        result (Dict[str, Any]): Dictionary with:
            - "session_id" (str): The manifest's session identifier.
            - "processed_files" (Dict[str, str]): Mapping of output types ("audio", "transcript", "slides", "exam") to their file paths in the cache for inputs that were present and processed.
            - "normalized_manifest" (str): Path to the written normalized manifest JSON in the cache.
    """
    from examkit.ingestion.transcript_normalizer import normalize_transcript
    from examkit.ingestion.slides_parser import parse_slides
    from examkit.ingestion.exam_parser import parse_exam

    # Validate manifest
    validate_manifest(manifest)

    session_id = manifest["session_id"]
    inputs = manifest["inputs"]
    ensure_dir(cache_dir)

    result = {
        "session_id": session_id,
        "processed_files": {}
    }

    logger.info(f"Processing session: {session_id}")

    # Process video (extract audio)
    if "video" in inputs and inputs["video"]:
        video_path = Path(inputs["video"])
        if video_path.exists():
            audio_path = cache_dir / f"{session_id}_audio.wav"
            extract_audio_from_video(video_path, audio_path, logger)
            result["processed_files"]["audio"] = str(audio_path)
        else:
            logger.warning(f"Video file not found: {video_path}")

    # Process transcript
    if "transcript" in inputs and inputs["transcript"]:
        transcript_path = Path(inputs["transcript"])
        if transcript_path.exists():
            normalized = normalize_transcript(transcript_path, logger)
            output_path = cache_dir / f"{session_id}_transcript.jsonl"
            from examkit.utils.io_utils import write_jsonl
            write_jsonl(normalized, output_path)
            result["processed_files"]["transcript"] = str(output_path)
            logger.info(f"Normalized {len(normalized)} transcript segments")
        else:
            logger.warning(f"Transcript file not found: {transcript_path}")

    # Process slides
    if "slides" in inputs and inputs["slides"]:
        slides_path = Path(inputs["slides"])
        if slides_path.exists():
            slides_data = parse_slides(slides_path, cache_dir, logger)
            output_path = cache_dir / f"{session_id}_slides.jsonl"
            from examkit.utils.io_utils import write_jsonl
            write_jsonl(slides_data, output_path)
            result["processed_files"]["slides"] = str(output_path)
            logger.info(f"Parsed {len(slides_data)} slides")
        else:
            logger.warning(f"Slides file not found: {slides_path}")

    # Process exam
    if "exam" in inputs and inputs["exam"]:
        exam_path = Path(inputs["exam"])
        if exam_path.exists():
            exam_data = parse_exam(exam_path, logger)
            output_path = cache_dir / f"{session_id}_exam.jsonl"
            from examkit.utils.io_utils import write_jsonl
            write_jsonl(exam_data, output_path)
            result["processed_files"]["exam"] = str(output_path)
            logger.info(f"Parsed {len(exam_data)} exam questions")
        else:
            logger.warning(f"Exam file not found: {exam_path}")

    # Save normalized manifest
    normalized_manifest_path = cache_dir / f"{session_id}_manifest.json"
    write_json(result, normalized_manifest_path)
    result["normalized_manifest"] = str(normalized_manifest_path)

    logger.info("Ingestion pipeline complete")
    return result