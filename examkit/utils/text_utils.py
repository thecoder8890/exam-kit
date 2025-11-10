"""
Text processing utilities.
"""

import re
from typing import List


def clean_text(text: str) -> str:
    """
    Normalize input text by collapsing consecutive whitespace into single spaces, removing control characters in the ranges \x00-\x1f and \x7f-\x9f, and trimming leading and trailing whitespace.
    
    Parameters:
        text (str): Input text to clean.
    
    Returns:
        str: Cleaned text with normalized whitespace and control characters removed.
    """
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove control characters
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    return text.strip()


def split_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences using punctuation (., !, ?) followed by whitespace.
    
    Parameters:
        text (str): Input text to segment.
    
    Returns:
        List[str]: Sentence strings with surrounding whitespace removed; empty segments are omitted.
    """
    # Simple sentence splitting (can be improved with spaCy)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def split_into_paragraphs(text: str) -> List[str]:
    """
    Split text into paragraphs by using double-newline boundaries and trimming each paragraph.
    
    Parameters:
        text (str): Text to split into paragraphs.
    
    Returns:
        List[str]: Non-empty paragraphs with surrounding whitespace removed.
    """
    paragraphs = text.split('\n\n')
    return [p.strip() for p in paragraphs if p.strip()]


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to at most max_length characters, appending a suffix when truncation occurs.
    
    Parameters:
        text (str): Input text to truncate.
        max_length (int): Maximum allowed length of the returned string.
        suffix (str): Suffix to append when truncation occurs (default "...").
    
    Returns:
        str: The original text if its length is <= max_length, otherwise a truncated string of length max_length that ends with the given suffix.
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """
    Extract unique candidate keywords from the given text.
    
    Parameters:
        text (str): Input text to extract keywords from.
        min_length (int): Minimum number of characters a token must have to be considered a keyword.
    
    Returns:
        List[str]: A list of unique keyword strings (order not guaranteed).
    """
    # Remove punctuation and split
    words = re.findall(r'\b\w+\b', text.lower())
    # Filter by length and common words
    stopwords = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'a', 'an'}
    keywords = [w for w in words if len(w) >= min_length and w not in stopwords]
    return list(set(keywords))


def normalize_whitespace(text: str) -> str:
    """
    Collapse all consecutive whitespace characters into single ASCII spaces and remove leading/trailing whitespace.
    
    Parameters:
        text (str): Input string that may contain spaces, tabs, newlines, or other whitespace characters.
    
    Returns:
        str: String where runs of whitespace are replaced by a single space and leading/trailing whitespace is removed.
    """
    return ' '.join(text.split())


def remove_urls(text: str) -> str:
    """
    Remove HTTP(S) and www-prefixed URLs from the given text.
    
    Returns:
        Text with HTTP(S) and www-prefixed URLs removed.
    """
    url_pattern = r'https?://\S+|www\.\S+'
    return re.sub(url_pattern, '', text)


def count_words(text: str) -> int:
    """
    Count the number of whitespace-separated tokens in the given text.
    
    Parameters:
        text (str): Input string whose words are counted; splitting is performed on any whitespace.
    
    Returns:
        word_count (int): Number of whitespace-separated tokens in text.
    """
    return len(text.split())