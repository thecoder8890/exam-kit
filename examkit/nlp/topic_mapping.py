"""
Topic mapping and coverage analysis.
"""

import logging
from typing import Any, Dict, List

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def load_topics(topics_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normalize a list of topic dictionaries into a consistent structure.
    
    Parameters:
        topics_data (List[Dict[str, Any]]): List of topic objects. Each object may include
            the keys `id`, `name`, `keywords`, `weight`, and `description`. If `id` is missing,
            a fallback ID is derived from `name` (lowercased, spaces replaced with underscores).
    
    Returns:
        List[Dict[str, Any]]: A list of normalized topic dictionaries, each containing the keys
        `id`, `name`, `keywords`, `weight`, and `description` with sensible defaults when absent.
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
    Assigns chunks to topics based on cosine similarity between their embeddings.
    
    Compares each chunk embedding to each topic embedding and adds a chunk's index to a topic's list when the cosine similarity is greater than or equal to the threshold.
    
    Parameters:
        chunks: List of chunk dictionaries (used for indexing; chunk content is not inspected).
        topics: List of topic dictionaries; each must include an "id" key.
        chunk_embeddings: 2D array of shape (num_chunks, embedding_dim).
        topic_embeddings: 2D array of shape (num_topics, embedding_dim).
        threshold (float): Minimum cosine similarity required to assign a chunk to a topic.
        logger (logging.Logger, optional): If provided, logs the number of chunks mapped per topic.
    
    Returns:
        Dict[str, List[int]]: Mapping from topic ID to a list of chunk indices assigned to that topic.
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
    Compute per-topic coverage metrics from a mapping of topic IDs to chunk indices.
    
    Parameters:
        topic_mapping (Dict[str, List[int]]): Mapping from topic ID to list of chunk indices assigned to that topic.
        topics (List[Dict[str, Any]]): List of topic dictionaries; each must include `"id"` and `"name"`, and may include `"weight"`.
        total_chunks (int): Total number of chunks considered; when zero or less, coverage percentages are reported as 0.0.
    
    Returns:
        List[Dict[str, Any]]: A list of per-topic coverage dictionaries containing:
            - topic_id (str): The topic's identifier.
            - name (str): The topic's display name.
            - chunk_count (int): Number of chunks mapped to the topic.
            - coverage_percentage (float): Percentage of total_chunks mapped to the topic (0.0–100.0).
            - weight (float): Topic weight (defaults to 1.0 if missing).
            - weighted_coverage (float): coverage_percentage multiplied by weight.
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
    Identify topic names whose coverage percentage is below a minimum threshold.
    
    Parameters:
        coverage_data (List[Dict[str, Any]]): Per-topic coverage dictionaries containing at least the keys "name" and "coverage_percentage".
        min_coverage (float): Coverage percentage threshold; topics with coverage strictly less than this value are considered gaps.
    
    Returns:
        List[str]: Names of topics whose coverage percentage is less than min_coverage.
    """
    gaps = []
    for item in coverage_data:
        if item["coverage_percentage"] < min_coverage:
            gaps.append(item["name"])
    return gaps