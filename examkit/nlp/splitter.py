"""
Text splitting for sentences and paragraphs.
"""

import logging
from typing import Any, Dict, List

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False


def load_spacy_model(model_name: str = "en_core_web_sm", logger: logging.Logger = None):
    """
    Load spaCy model.

    Args:
        model_name: SpaCy model name.
        logger: Logger instance.

    Returns:
        Loaded spaCy model.
    """
    if not SPACY_AVAILABLE:
        raise ImportError("spaCy not available. Install with: pip install spacy")

    try:
        nlp = spacy.load(model_name)
        if logger:
            logger.info(f"Loaded spaCy model: {model_name}")
        return nlp
    except OSError:
        if logger:
            logger.error(f"spaCy model '{model_name}' not found. Install with: python -m spacy download {model_name}")
        raise


def split_into_sentences_spacy(text: str, nlp) -> List[str]:
    """
    Split text into sentences using spaCy.

    Args:
        text: Input text.
        nlp: SpaCy model.

    Returns:
        List of sentences.
    """
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents]


def split_into_chunks(
    segments: List[Dict[str, Any]],
    max_chunk_size: int = 500,
    logger: logging.Logger = None
) -> List[Dict[str, Any]]:
    """
    Split segments into manageable chunks for embedding.

    Args:
        segments: List of text segments.
        max_chunk_size: Maximum chunk size in characters.
        logger: Logger instance.

    Returns:
        List of chunked segments.
    """
    chunks = []

    for segment in segments:
        text = segment.get("text", "")

        if len(text) <= max_chunk_size:
            chunks.append(segment)
        else:
            # Split long text into smaller chunks
            words = text.split()
            current_chunk = []
            current_length = 0

            for word in words:
                word_length = len(word) + 1  # +1 for space
                if current_length + word_length > max_chunk_size and current_chunk:
                    # Create chunk
                    chunk_text = ' '.join(current_chunk)
                    chunk = segment.copy()
                    chunk["text"] = chunk_text
                    chunk["is_split"] = True
                    chunks.append(chunk)

                    current_chunk = [word]
                    current_length = word_length
                else:
                    current_chunk.append(word)
                    current_length += word_length

            # Add remaining chunk
            if current_chunk:
                chunk_text = ' '.join(current_chunk)
                chunk = segment.copy()
                chunk["text"] = chunk_text
                chunk["is_split"] = True
                chunks.append(chunk)

    if logger:
        logger.info(f"Split {len(segments)} segments into {len(chunks)} chunks")

    return chunks


def merge_short_segments(
    segments: List[Dict[str, Any]],
    min_length: int = 50
) -> List[Dict[str, Any]]:
    """
    Merge very short segments for better context.

    Args:
        segments: List of segments.
        min_length: Minimum segment length.

    Returns:
        List of merged segments.
    """
    if not segments:
        return []

    merged = []
    buffer = []

    for segment in segments:
        text = segment.get("text", "")

        if len(text) < min_length:
            buffer.append(segment)
        else:
            if buffer:
                # Merge buffer segments
                merged_text = ' '.join([s.get("text", "") for s in buffer])
                merged_segment = buffer[0].copy()
                merged_segment["text"] = merged_text
                merged_segment["is_merged"] = True
                merged.append(merged_segment)
                buffer = []

            merged.append(segment)

    # Handle remaining buffer
    if buffer:
        merged_text = ' '.join([s.get("text", "") for s in buffer])
        merged_segment = buffer[0].copy()
        merged_segment["text"] = merged_text
        merged_segment["is_merged"] = True
        merged.append(merged_segment)

    return merged
