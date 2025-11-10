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
    Extract named entities from text and return them as dictionaries.
    
    If spaCy is unavailable (module-level SPACY_AVAILABLE is False), returns an empty list.
    
    Parameters:
        text (str): Text to analyze.
        nlp: A spaCy language model used to create a Doc for extraction.
        logger (logging.Logger, optional): If provided, receives a debug message with the count of extracted entities.
    
    Returns:
        List[dict]: A list of entity dictionaries, each containing:
            - "text": the entity string as found in the input,
            - "label": the entity label (spaCy label string),
            - "start": start character offset of the entity,
            - "end": end character offset of the entity.
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
    Clean and tokenize text into lowercase tokens, removing punctuation and whitespace.
    
    Parameters:
        text (str): Input text to process.
        remove_stopwords (bool): If True, omit spaCy stopwords from the output.
    
    Returns:
        List[str]: Cleaned, tokenized, lowercase tokens. If spaCy is unavailable, returns text.split().
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
    Extract noun phrase key phrases from the given text.
    
    If spaCy is unavailable, returns an empty list. The returned list contains unique noun phrases found in the text, limited to at most `top_n` items.
    
    Parameters:
        nlp: SpaCy language model used to parse the text.
        top_n (int): Maximum number of phrases to return.
    
    Returns:
        List of unique noun phrases, limited to `top_n` items.
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
    Return the input text with each token replaced by its lemma.
    
    If spaCy is unavailable, the original text is returned.
    
    Returns:
        Lemmatized text with tokens' lemmas joined by single spaces.
    """
    if not SPACY_AVAILABLE:
        return text

    doc = nlp(text)
    lemmas = [token.lemma_ for token in doc if not token.is_punct and not token.is_space]
    return ' '.join(lemmas)


def detect_language_patterns(text: str, nlp) -> Dict[str, Any]:
    """
    Analyze text to extract basic language structure and pattern metrics.
    
    Parameters:
        text (str): Text to analyze.
        nlp: spaCy language model used to parse the text.
    
    Returns:
        patterns (Dict[str, Any]): Mapping with the following keys:
            - "sentence_count": Number of sentences in the text.
            - "token_count": Total number of tokens.
            - "has_questions": `true` if the text contains a question mark, `false` otherwise.
            - "has_imperatives": `true` if any sentence appears to start with a base-form verb, `false` otherwise.
            - "noun_phrases": Number of noun phrase chunks.
            - "entities": Number of named entities detected.
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