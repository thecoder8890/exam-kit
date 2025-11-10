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
    Retrieve context chunks relevant to a topic.
    
    Parameters:
        topic (dict): Topic object with at least a `name` key. May include `description` (str) and `keywords` (List[str]) to enrich the query.
        model: Embedding model used for similarity search.
        index: Vector index used for retrieval.
        chunks_metadata (List[dict]): List of candidate chunk metadata to search over.
        top_k (int): Maximum number of chunks to return.
        logger (logging.Logger, optional): Logger for debug messages.
    
    Returns:
        List[dict]: Chunks ranked by relevance to the topic. Each item is a metadata dictionary typically containing fields such as `text`, `source`, and `distance`.
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
    Remove duplicate chunks by exact text match, preserving the first occurrence order.
    
    Parameters:
        chunks (List[Dict[str, Any]]): Sequence of chunk dictionaries that may contain a "text" field.
        similarity_threshold (float): Currently unused; kept for API compatibility.
    
    Returns:
        List[Dict[str, Any]]: Deduplicated list where later chunks with the same "text" as an earlier chunk are removed.
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
    Reorder a list of chunks to increase diversity of their originating sources.
    
    Parameters:
        chunks (List[Dict[str, Any]]): Chunks containing at least a "source" field.
        prefer_exam (bool): If True, prioritize sources in the order ["exam", "slides", "transcript", "asr"]; if False, use ["slides", "transcript", "exam", "asr"].
    
    Returns:
        List[Dict[str, Any]]: The input chunks re-ranked by interleaving items from prioritized sources; chunks from sources not in the priority list are appended at the end.
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
    Filter chunks to those whose distance score lies within the inclusive range.
    
    Chunks missing a "distance" field are treated as having distance 999 and will be excluded unless the range includes that value.
    
    Parameters:
        chunks: Iterable of chunk dictionaries; each chunk's "distance" key is used for filtering.
        min_distance: Minimum acceptable distance (inclusive).
        max_distance: Maximum acceptable distance (inclusive).
    
    Returns:
        Filtered list of chunks whose "distance" is between min_distance and max_distance, inclusive.
    """
    return [
        chunk for chunk in chunks
        if min_distance <= chunk.get("distance", 999) <= max_distance
    ]