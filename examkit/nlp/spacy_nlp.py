"""
spaCy NLP utilities for NER and text cleanup.
"""

import logging
from typing import Any, Dict, List

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False


def extract_named_entities(text: str, nlp, logger: logging.Logger = None) -> List[Dict[str, Any]]:
    """
    Extract named entities from text using spaCy.

    Args:
        text: Input text.
        nlp: SpaCy model.
        logger: Logger instance.

    Returns:
        List of named entities with labels.
    """
    if not SPACY_AVAILABLE:
        return []

    doc = nlp(text)
    entities = []

    for ent in doc.ents:
        entities.append({
            "text": ent.text,
            "label": ent.label_,
            "start": ent.start_char,
            "end": ent.end_char
        })

    if logger:
        logger.debug(f"Extracted {len(entities)} entities from text")

    return entities


def clean_and_tokenize(text: str, nlp, remove_stopwords: bool = False) -> List[str]:
    """
    Clean and tokenize text using spaCy.

    Args:
        text: Input text.
        nlp: SpaCy model.
        remove_stopwords: Whether to remove stopwords.

    Returns:
        List of tokens.
    """
    if not SPACY_AVAILABLE:
        return text.split()

    doc = nlp(text)
    tokens = []

    for token in doc:
        if token.is_punct or token.is_space:
            continue
        if remove_stopwords and token.is_stop:
            continue
        tokens.append(token.text.lower())

    return tokens


def extract_key_phrases(text: str, nlp, top_n: int = 10) -> List[str]:
    """
    Extract key noun phrases from text.

    Args:
        text: Input text.
        nlp: SpaCy model.
        top_n: Number of phrases to return.

    Returns:
        List of key phrases.
    """
    if not SPACY_AVAILABLE:
        return []

    doc = nlp(text)
    phrases = []

    # Extract noun chunks
    for chunk in doc.noun_chunks:
        phrases.append(chunk.text)

    # Return unique phrases, limited to top_n
    return list(set(phrases))[:top_n]


def lemmatize_text(text: str, nlp) -> str:
    """
    Lemmatize text using spaCy.

    Args:
        text: Input text.
        nlp: SpaCy model.

    Returns:
        Lemmatized text.
    """
    if not SPACY_AVAILABLE:
        return text

    doc = nlp(text)
    lemmas = [token.lemma_ for token in doc if not token.is_punct and not token.is_space]
    return ' '.join(lemmas)


def detect_language_patterns(text: str, nlp) -> Dict[str, Any]:
    """
    Detect language patterns and structure.

    Args:
        text: Input text.
        nlp: SpaCy model.

    Returns:
        Dictionary with language pattern information.
    """
    if not SPACY_AVAILABLE:
        return {}

    doc = nlp(text)

    patterns = {
        "sentence_count": len(list(doc.sents)),
        "token_count": len(doc),
        "has_questions": "?" in text,
        "has_imperatives": any(token.tag_ == "VB" and token.i == 0 for sent in doc.sents for token in sent),
        "noun_phrases": len(list(doc.noun_chunks)),
        "entities": len(doc.ents)
    }

    return patterns
