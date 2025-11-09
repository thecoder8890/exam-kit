"""
Topic mapping and coverage analysis.
"""

import logging
from typing import Any, Dict, List

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def load_topics(topics_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Load and normalize topics.

    Args:
        topics_data: List of topic dictionaries.

    Returns:
        Normalized topics list.
    """
    normalized = []
    for topic in topics_data:
        normalized.append({
            "id": topic.get("id", topic.get("name", "").lower().replace(" ", "_")),
            "name": topic.get("name", ""),
            "keywords": topic.get("keywords", []),
            "weight": topic.get("weight", 1.0),
            "description": topic.get("description", "")
        })
    return normalized


def map_chunks_to_topics(
    chunks: List[Dict[str, Any]],
    topics: List[Dict[str, Any]],
    chunk_embeddings: np.ndarray,
    topic_embeddings: np.ndarray,
    threshold: float = 0.3,
    logger: logging.Logger = None
) -> Dict[str, List[int]]:
    """
    Map text chunks to topics using embeddings.

    Args:
        chunks: List of text chunks.
        topics: List of topics.
        chunk_embeddings: Embeddings for chunks.
        topic_embeddings: Embeddings for topics.
        threshold: Similarity threshold.
        logger: Logger instance.

    Returns:
        Dictionary mapping topic IDs to chunk indices.
    """
    # Calculate similarity matrix
    similarities = cosine_similarity(chunk_embeddings, topic_embeddings)

    # Map chunks to topics
    topic_mapping = {topic["id"]: [] for topic in topics}

    for chunk_idx, sim_scores in enumerate(similarities):
        for topic_idx, score in enumerate(sim_scores):
            if score >= threshold:
                topic_id = topics[topic_idx]["id"]
                topic_mapping[topic_id].append(chunk_idx)

    if logger:
        for topic_id, chunk_indices in topic_mapping.items():
            logger.info(f"Topic '{topic_id}': {len(chunk_indices)} chunks mapped")

    return topic_mapping


def calculate_coverage(
    topic_mapping: Dict[str, List[int]],
    topics: List[Dict[str, Any]],
    total_chunks: int
) -> List[Dict[str, Any]]:
    """
    Calculate topic coverage metrics.

    Args:
        topic_mapping: Mapping of topics to chunk indices.
        topics: List of topics.
        total_chunks: Total number of chunks.

    Returns:
        List of coverage metrics per topic.
    """
    coverage_data = []

    for topic in topics:
        topic_id = topic["id"]
        mapped_chunks = topic_mapping.get(topic_id, [])
        chunk_count = len(mapped_chunks)
        coverage_pct = (chunk_count / total_chunks * 100) if total_chunks > 0 else 0.0

        coverage_data.append({
            "topic_id": topic_id,
            "name": topic["name"],
            "chunk_count": chunk_count,
            "coverage_percentage": coverage_pct,
            "weight": topic.get("weight", 1.0),
            "weighted_coverage": coverage_pct * topic.get("weight", 1.0)
        })

    return coverage_data


def identify_gaps(
    coverage_data: List[Dict[str, Any]],
    min_coverage: float = 10.0
) -> List[str]:
    """
    Identify topics with insufficient coverage.

    Args:
        coverage_data: List of coverage metrics.
        min_coverage: Minimum acceptable coverage percentage.

    Returns:
        List of under-covered topic names.
    """
    gaps = []
    for item in coverage_data:
        if item["coverage_percentage"] < min_coverage:
            gaps.append(item["name"])
    return gaps
