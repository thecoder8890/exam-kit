"""
Text processing utilities.
"""

import re
from typing import List


def clean_text(text: str) -> str:
    """
    Clean and normalize text.

    Args:
        text: Input text.

    Returns:
        Cleaned text.
    """
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove control characters
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    return text.strip()


def split_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences using basic heuristics.

    Args:
        text: Input text.

    Returns:
        List of sentences.
    """
    # Simple sentence splitting (can be improved with spaCy)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def split_into_paragraphs(text: str) -> List[str]:
    """
    Split text into paragraphs.

    Args:
        text: Input text.

    Returns:
        List of paragraphs.
    """
    paragraphs = text.split('\n\n')
    return [p.strip() for p in paragraphs if p.strip()]


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.

    Args:
        text: Input text.
        max_length: Maximum length.
        suffix: Suffix to add if truncated.

    Returns:
        Truncated text.
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """
    Extract potential keywords from text (simple implementation).

    Args:
        text: Input text.
        min_length: Minimum keyword length.

    Returns:
        List of keywords.
    """
    # Remove punctuation and split
    words = re.findall(r'\b\w+\b', text.lower())
    # Filter by length and common words
    stopwords = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'a', 'an'}
    keywords = [w for w in words if len(w) >= min_length and w not in stopwords]
    return list(set(keywords))


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text.

    Args:
        text: Input text.

    Returns:
        Text with normalized whitespace.
    """
    return ' '.join(text.split())


def remove_urls(text: str) -> str:
    """
    Remove URLs from text.

    Args:
        text: Input text.

    Returns:
        Text with URLs removed.
    """
    url_pattern = r'https?://\S+|www\.\S+'
    return re.sub(url_pattern, '', text)


def count_words(text: str) -> int:
    """
    Count words in text.

    Args:
        text: Input text.

    Returns:
        Word count.
    """
    return len(text.split())
