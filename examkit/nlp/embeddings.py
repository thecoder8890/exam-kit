"""
Embeddings generation using sentence-transformers and FAISS indexing.
"""

import logging
import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False


def load_embedding_model(model_name: str = "all-MiniLM-L6-v2", logger: logging.Logger = None):
    """
    Load sentence-transformers model.

    Args:
        model_name: Model name.
        logger: Logger instance.

    Returns:
        Loaded model.
    """
    if not SENTENCE_TRANSFORMERS_AVAILABLE:
        raise ImportError("sentence-transformers not available")

    if logger:
        logger.info(f"Loading embedding model: {model_name}")

    model = SentenceTransformer(model_name)
    return model


def generate_embeddings(
    texts: List[str],
    model,
    batch_size: int = 32,
    logger: logging.Logger = None
) -> np.ndarray:
    """
    Generate embeddings for a list of texts.

    Args:
        texts: List of text strings.
        model: SentenceTransformer model.
        batch_size: Batch size for encoding.
        logger: Logger instance.

    Returns:
        Numpy array of embeddings.
    """
    if logger:
        logger.info(f"Generating embeddings for {len(texts)} texts")

    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True
    )

    return embeddings


def create_faiss_index(
    embeddings: np.ndarray,
    dim: int,
    logger: logging.Logger = None
) -> Any:
    """
    Create FAISS index from embeddings.

    Args:
        embeddings: Numpy array of embeddings.
        dim: Embedding dimension.
        logger: Logger instance.

    Returns:
        FAISS index.
    """
    if not FAISS_AVAILABLE:
        raise ImportError("faiss not available")

    if logger:
        logger.info(f"Creating FAISS index with {len(embeddings)} vectors")

    # Use flat L2 index for simplicity
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings.astype('float32'))

    return index


def save_index(index: Any, index_path: Path, metadata: Dict[str, Any], metadata_path: Path) -> None:
    """
    Save FAISS index and metadata.

    Args:
        index: FAISS index.
        index_path: Path to save index.
        metadata: Metadata dictionary.
        metadata_path: Path to save metadata.
    """
    # Save FAISS index
    faiss.write_index(index, str(index_path))

    # Save metadata
    with open(metadata_path, 'wb') as f:
        pickle.dump(metadata, f)


def load_index(index_path: Path, metadata_path: Path) -> tuple:
    """
    Load FAISS index and metadata.

    Args:
        index_path: Path to FAISS index.
        metadata_path: Path to metadata file.

    Returns:
        Tuple of (index, metadata).
    """
    index = faiss.read_index(str(index_path))

    with open(metadata_path, 'rb') as f:
        metadata = pickle.load(f)

    return index, metadata


def search_similar(
    query: str,
    model,
    index: Any,
    metadata: List[Dict[str, Any]],
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Search for similar texts using FAISS.

    Args:
        query: Query text.
        model: SentenceTransformer model.
        index: FAISS index.
        metadata: List of metadata dicts for each indexed text.
        top_k: Number of results to return.

    Returns:
        List of similar items with scores.
    """
    # Generate query embedding
    query_embedding = model.encode([query], convert_to_numpy=True)

    # Search
    distances, indices = index.search(query_embedding.astype('float32'), top_k)

    # Prepare results
    results = []
    for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
        result = metadata[idx].copy()
        result["distance"] = float(dist)
        result["rank"] = i + 1
        results.append(result)

    return results
