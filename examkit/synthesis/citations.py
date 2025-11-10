"""
Citation management for tracking sources.
"""

import logging
from typing import Any, Dict, List

from examkit.utils.timecode import seconds_to_timecode


class CitationManager:
    """Manages citations for generated content."""

    def __init__(self):
        """
        Initialize the CitationManager's internal state.
        
        Sets up an empty list for stored citations and initializes the citation counter to 0.
        """
        self.citations = []
        self.citation_counter = 0

    def add_citation(
        self,
        source_type: str,
        source_id: str,
        content: str,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Add a citation to the manager and generate a unique citation ID.
        
        Parameters:
            source_type (str): Source kind (e.g., "video", "slide", "exam").
            source_id (str): Identifier of the source.
            content (str): The cited content or excerpt.
            metadata (Dict[str, Any], optional): Additional citation metadata; defaults to empty dict.
        
        Returns:
            str: Generated citation ID (e.g., "cite_1").
        """
        self.citation_counter += 1
        citation_id = f"cite_{self.citation_counter}"

        citation = {
            "id": citation_id,
            "type": source_type,
            "source_id": source_id,
            "content": content,
            "metadata": metadata or {}
        }

        self.citations.append(citation)
        return citation_id

    def format_citation(self, chunk: Dict[str, Any]) -> str:
        """
        Return a formatted citation label for a content chunk.
        
        Parameters:
            chunk (Dict[str, Any]): Dictionary describing the source. Recognized keys:
                - "source": source type (e.g., "transcript", "asr", "slides", "exam", or other).
                - For "transcript"/"asr": optional "start" (seconds) to include a timecode.
                - For "slides": optional "slide_number".
                - For "exam": optional "question_id".
        
        Returns:
            str: A citation string in one of the formats:
                - "[vid {timecode}]" if a transcript/asr chunk includes a start time.
                - "[vid]" for transcript/asr without a start time.
                - "[slide {slide_number}]" for slide chunks.
                - "[exam {question_id}]" for exam chunks.
                - "[{source}]" for any other source type.
        """
        source_type = chunk.get("source", "unknown")

        if source_type == "transcript" or source_type == "asr":
            # Video citation with timecode
            start = chunk.get("start")
            if start is not None:
                timecode = seconds_to_timecode(start)
                return f"[vid {timecode}]"
            return "[vid]"

        elif source_type == "slides":
            # Slide citation
            slide_num = chunk.get("slide_number", "?")
            return f"[slide {slide_num}]"

        elif source_type == "exam":
            # Exam question citation
            question_id = chunk.get("question_id", "?")
            return f"[exam {question_id}]"

        else:
            return f"[{source_type}]"

    def format_multiple_citations(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Create a single citation string from multiple chunk descriptors.
        
        Formats each chunk using format_citation, removes duplicate formatted citations while preserving their original order, and joins them with a single space.
        
        Parameters:
            chunks (List[Dict[str, Any]]): List of chunk dictionaries describing sources (e.g., transcript, slides, exam).
        
        Returns:
            str: Space-separated string of unique formatted citations in original order.
        """
        citations = []
        for chunk in chunks:
            citation = self.format_citation(chunk)
            if citation not in citations:
                citations.append(citation)

        return " ".join(citations)

    def export_citations(self) -> List[Dict[str, Any]]:
        """
        Retrieve all stored citation records.
        
        Returns:
            List[Dict[str, Any]]: The internal list of citation dictionaries. Each dictionary contains the keys
            `id`, `type`, `source_id`, `content`, and `metadata`. This returns the actual internal list (not a copy).
        """
        return self.citations

    def get_citation_by_id(self, citation_id: str) -> Dict[str, Any]:
        """
        Retrieve a stored citation by its identifier.
        
        Parameters:
            citation_id (str): The citation identifier to look up.
        
        Returns:
            dict: The citation dictionary if found, or `None` if no matching citation exists.
        """
        for citation in self.citations:
            if citation["id"] == citation_id:
                return citation
        return None

    def get_citations_by_type(self, source_type: str) -> List[Dict[str, Any]]:
        """
        Return all stored citations whose "type" field matches the given source type.
        
        Parameters:
            source_type (str): The citation type to match.
        
        Returns:
            List[Dict[str, Any]]: List of citation dictionaries whose `"type"` equals `source_type`.
        """
        return [c for c in self.citations if c["type"] == source_type]

    def get_citation_count(self) -> int:
        """
        Get the number of stored citations.
        
        Returns:
            int: Number of citations currently tracked.
        """
        return len(self.citations)

    def clear(self) -> None:
        """
        Remove all stored citations and reset the internal citation counter to zero.
        """
        self.citations = []
        self.citation_counter = 0