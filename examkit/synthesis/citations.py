"""
Citation management for tracking sources.
"""

import logging
from typing import Any, Dict, List

from examkit.utils.timecode import seconds_to_timecode


class CitationManager:
    """Manages citations for generated content."""

    def __init__(self):
        """Initialize citation manager."""
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
        Add a citation and return citation ID.

        Args:
            source_type: Type of source (video, slide, exam, etc.).
            source_id: Identifier for the source.
            content: Content being cited.
            metadata: Additional metadata.

        Returns:
            Citation ID.
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
        Format a citation string from a chunk.

        Args:
            chunk: Chunk dictionary with source information.

        Returns:
            Formatted citation string.
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
        Format multiple citations from chunks.

        Args:
            chunks: List of chunks.

        Returns:
            Formatted citation string combining all sources.
        """
        citations = []
        for chunk in chunks:
            citation = self.format_citation(chunk)
            if citation not in citations:
                citations.append(citation)

        return " ".join(citations)

    def export_citations(self) -> List[Dict[str, Any]]:
        """
        Export all citations.

        Returns:
            List of citation dictionaries.
        """
        return self.citations

    def get_citation_by_id(self, citation_id: str) -> Dict[str, Any]:
        """
        Get citation by ID.

        Args:
            citation_id: Citation identifier.

        Returns:
            Citation dictionary or None.
        """
        for citation in self.citations:
            if citation["id"] == citation_id:
                return citation
        return None

    def get_citations_by_type(self, source_type: str) -> List[Dict[str, Any]]:
        """
        Get all citations of a specific type.

        Args:
            source_type: Type of source.

        Returns:
            List of citations.
        """
        return [c for c in self.citations if c["type"] == source_type]

    def get_citation_count(self) -> int:
        """
        Get total number of citations.

        Returns:
            Citation count.
        """
        return len(self.citations)

    def clear(self) -> None:
        """Clear all citations."""
        self.citations = []
        self.citation_counter = 0
