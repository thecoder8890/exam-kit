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
    Load and return a spaCy language model by name.
    
    Parameters:
        model_name (str): Name of the spaCy model to load (e.g., "en_core_web_sm").
        logger (logging.Logger, optional): Logger for informational and error messages.
    
    Returns:
        nlp: Loaded spaCy language object.
    
    Raises:
        ImportError: If spaCy is not installed.
        OSError: If the specified model is not found.
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
    Split the input text into sentence strings using a spaCy pipeline.
    
    Parameters:
        text (str): Text to segment into sentences.
        nlp: A spaCy language pipeline or model (e.g., the object returned by `spacy.load(...)`) used to perform sentence segmentation.
    
    Returns:
        List[str]: Sentence strings extracted from the text, each stripped of surrounding whitespace.
    """
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents]


def split_into_chunks(
    segments: List[Dict[str, Any]],
    max_chunk_size: int = 500,
    logger: logging.Logger = None
) -> List[Dict[str, Any]]:
    """
    Breaks segments into character-limited chunks by splitting long texts at word boundaries.
    
    Long segments (text length > max_chunk_size) are split into smaller chunks that copy the original segment, set the chunked text under the "text" key, and mark the chunk with "is_split" = True. Segments whose text length is less than or equal to max_chunk_size are returned unchanged.
    
    Parameters:
        segments (List[Dict[str, Any]]): List of segment dictionaries; each dictionary is expected to contain a "text" key.
        max_chunk_size (int): Maximum allowed chunk size in characters.
        logger (logging.Logger, optional): Optional logger used to record chunking summary.
    
    Returns:
        List[Dict[str, Any]]: List of segment dictionaries including original and generated chunk dictionaries (generated chunks have "is_split" = True).
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
    Merge consecutive short text segments into larger segments to preserve context.
    
    Segments with a "text" length less than `min_length` are concatenated (space-separated) into a single segment. The merged segment is created by copying the first buffered segment, replacing its "text" with the concatenated text and setting "is_merged" to True.
    
    Parameters:
        segments (List[Dict[str, Any]]): List of segment dictionaries; each should contain a "text" key.
        min_length (int): Minimum number of characters for a segment to be considered "long" and not merged.
    
    Returns:
        List[Dict[str, Any]]: A list of segments where consecutive short segments have been merged. Merged segments include an "is_merged" key set to True.
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