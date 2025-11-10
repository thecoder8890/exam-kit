"""
RAG retrieval utilities.
"""

import logging
from typing import Any, Dict, List

from examkit.nlp.embeddings import search_similar


def retrieve_context_for_topic(
    topic: Dict[str, Any],
    model,
    index: Any,
    chunks_metadata: List[Dict[str, Any]],
    top_k: int = 8,
    logger: logging.Logger = None
) -> List[Dict[str, Any]]:
    """
    Retrieve relevant context chunks for a topic.

    Args:
        topic: Topic dictionary.
        model: Embedding model.
        index: FAISS index.
        chunks_metadata: Metadata for all chunks.
        top_k: Number of chunks to retrieve.
        logger: Logger instance.

    Returns:
        List of relevant chunks with metadata.
    """
    # Create query from topic
    query = f"{topic['name']} {topic.get('description', '')} {' '.join(topic.get('keywords', []))}"

    if logger:
        logger.debug(f"Retrieving context for topic: {topic['name']}")

    # Search for similar chunks
    results = search_similar(query, model, index, chunks_metadata, top_k)

    return results


def deduplicate_chunks(chunks: List[Dict[str, Any]], similarity_threshold: float = 0.95) -> List[Dict[str, Any]]:
    """
    Remove duplicate or highly similar chunks.

    Args:
        chunks: List of chunks.
        similarity_threshold: Threshold for considering chunks as duplicates.

    Returns:
        Deduplicated chunks.
    """
    if not chunks:
        return []

    unique_chunks = [chunks[0]]

    for chunk in chunks[1:]:
        text = chunk.get("text", "")
        is_duplicate = False

        for unique_chunk in unique_chunks:
            unique_text = unique_chunk.get("text", "")
            # Simple similarity check based on text overlap
            if text == unique_text:
                is_duplicate = True
                break

        if not is_duplicate:
            unique_chunks.append(chunk)

    return unique_chunks


def rank_by_source_diversity(
    chunks: List[Dict[str, Any]],
    prefer_exam: bool = True
) -> List[Dict[str, Any]]:
    """
    Re-rank chunks to promote source diversity.

    Args:
        chunks: List of chunks with source information.
        prefer_exam: Whether to prioritize exam-related chunks.

    Returns:
        Re-ranked chunks.
    """
    if not chunks:
        return []

    # Group by source
    by_source = {}
    for chunk in chunks:
        source = chunk.get("source", "unknown")
        if source not in by_source:
            by_source[source] = []
        by_source[source].append(chunk)

    # Prioritize sources
    source_priority = ["exam", "slides", "transcript", "asr"]
    if not prefer_exam:
        source_priority = ["slides", "transcript", "exam", "asr"]

    # Interleave chunks from different sources
    reranked = []
    max_len = max(len(chunks_list) for chunks_list in by_source.values()) if by_source else 0

    for i in range(max_len):
        for source in source_priority:
            if source in by_source and i < len(by_source[source]):
                reranked.append(by_source[source][i])

    # Add any remaining chunks
    for source, chunks_list in by_source.items():
        if source not in source_priority:
            reranked.extend(chunks_list)

    return reranked


def filter_by_confidence(
    chunks: List[Dict[str, Any]],
    min_distance: float = 0.0,
    max_distance: float = 1.0
) -> List[Dict[str, Any]]:
    """
    Filter chunks by distance/confidence score.

    Args:
        chunks: List of chunks with distance scores.
        min_distance: Minimum distance threshold.
        max_distance: Maximum distance threshold.

    Returns:
        Filtered chunks.
    """
    return [
        chunk for chunk in chunks
        if min_distance <= chunk.get("distance", 999) <= max_distance
    ]
