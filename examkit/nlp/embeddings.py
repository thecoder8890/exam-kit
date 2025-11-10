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
    Load a SentenceTransformer embedding model by name.
    
    Parameters:
        model_name (str): Identifier of the SentenceTransformer model to load (e.g., "all-MiniLM-L6-v2").
    
    Returns:
        The instantiated `SentenceTransformer` model.
    
    Raises:
        ImportError: If the `sentence-transformers` package is not available.
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
    Generate embeddings for each input text using the provided sentence-transformer model.
    
    Each row in the returned array corresponds to the embedding for the text at the same position in `texts`, preserving order.
    
    Returns:
        np.ndarray: Array of embeddings where row i is the embedding for texts[i].
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
    Create a FAISS flat L2 index and add the provided embedding vectors.
    
    Parameters:
        embeddings (np.ndarray): Array of vectors to index.
        dim (int): Dimensionality of each embedding vector.
    
    Returns:
        faiss_index: FAISS IndexFlatL2 instance containing the provided vectors.
    
    Raises:
        ImportError: If `faiss` is not available.
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
    Persist a FAISS index and its associated metadata to disk.
    
    Parameters:
        index: FAISS index instance to save.
        index_path (Path): Filesystem path where the FAISS index file will be written.
        metadata (Dict[str, Any]): Dictionary of metadata associated with the index (for example, mapping vector identifiers to records).
        metadata_path (Path): Filesystem path where the metadata will be serialized and saved.
    """
    # Save FAISS index
    faiss.write_index(index, str(index_path))

    # Save metadata
    with open(metadata_path, 'wb') as f:
        pickle.dump(metadata, f)


def load_index(index_path: Path, metadata_path: Path) -> tuple:
    """
    Load a FAISS index and its associated metadata from disk.
    
    Parameters:
        index_path (Path): Path to the FAISS index file.
        metadata_path (Path): Path to the pickled metadata file.
    
    Returns:
        tuple: (index, metadata) where `index` is a FAISS Index instance and `metadata` is the Python object restored from the metadata file.
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
    Finds metadata entries most similar to a query using a FAISS index.
    
    Parameters:
        query (str): Text query to search for.
        model: SentenceTransformer instance used to encode the query into an embedding.
        index: FAISS index containing the indexed embeddings.
        metadata (List[Dict[str, Any]]): List of metadata dictionaries aligned by position with the indexed embeddings.
        top_k (int): Number of top results to return.
    
    Returns:
        List[Dict[str, Any]]: List of metadata dictionaries for the top matches, each augmented with:
            - "distance" (float): L2 distance between the query embedding and the matched vector.
            - "rank" (int): 1-based rank (1 is the closest).
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