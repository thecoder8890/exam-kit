"""
Configuration management using Pydantic models.
"""

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field


class ASRConfig(BaseModel):
    """Automatic Speech Recognition configuration."""

    engine: str = "faster-whisper"
    model: str = "small"
    language: str = "en"
    vad: bool = True


class LLMConfig(BaseModel):
    """Large Language Model configuration."""

    engine: str = "ollama"
    model: str = "llama3.2:8b"
    temperature: float = 0.2
    max_tokens: int = 900
    system_prompt: str = (
        "You create exam-ready, cited study notes. Be precise, concise, and grounded in sources."
    )


class EmbeddingConfig(BaseModel):
    """Embedding model configuration."""

    model: str = "all-MiniLM-L6-v2"
    dim: int = 384
    batch_size: int = 32


class RetrievalConfig(BaseModel):
    """RAG retrieval configuration."""

    top_k: int = 8
    max_context_tokens: int = 2000


class PDFConfig(BaseModel):
    """PDF rendering configuration."""

    engine: Literal["typst", "pandoc"] = "typst"
    theme: str = "classic"
    font_size: int = 11
    include_appendix: bool = True


class DiagramsConfig(BaseModel):
    """Diagram generation configuration."""

    graphviz: bool = True


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: str = "INFO"


class ExamKitConfig(BaseModel):
    """Main ExamKit configuration."""

    asr: ASRConfig = Field(default_factory=ASRConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    retrieval: RetrievalConfig = Field(default_factory=RetrievalConfig)
    pdf: PDFConfig = Field(default_factory=PDFConfig)
    diagrams: DiagramsConfig = Field(default_factory=DiagramsConfig)
    offline: bool = True
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

    @classmethod
    def from_yaml(cls, path: Path) -> "ExamKitConfig":
        """
        Load configuration from a YAML file.

        Args:
            path: Path to the YAML configuration file.

        Returns:
            ExamKitConfig instance.
        """
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return cls(**data)

    def to_yaml(self, path: Path) -> None:
        """
        Save configuration to a YAML file.

        Args:
            path: Path to save the YAML configuration file.
        """
        with open(path, "w") as f:
            yaml.dump(self.model_dump(), f, default_flow_style=False, sort_keys=False)
