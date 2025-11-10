"""
Content composer - main pipeline for building study materials.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List

from examkit.config import ExamKitConfig
from examkit.nlp.embeddings import load_embedding_model, generate_embeddings, create_faiss_index, save_index
from examkit.nlp.retrieval import retrieve_context_for_topic
from examkit.nlp.splitter import split_into_chunks
from examkit.nlp.topic_mapping import load_topics, map_chunks_to_topics, calculate_coverage
from examkit.synthesis.citations import CitationManager
from examkit.synthesis.ollama_client import generate_completion
from examkit.synthesis.prompts import (
    render_definition_prompt,
    render_derivation_prompt,
    render_mistakes_prompt,
    render_revision_prompt,
    render_example_prompt
)
from examkit.utils.io_utils import read_jsonl, read_json, write_json, write_text
from examkit.render.templater import render_markdown_document
from examkit.render.typst_renderer import compile_typst_to_pdf


def load_processed_data(session_id: str, cache_dir: Path, logger: logging.Logger) -> Dict[str, List]:
    """
    Load cached session data for transcripts, slides, and exam items.
    
    Reads JSONL files named <session_id>_transcript.jsonl, <session_id>_slides.jsonl,
    and <session_id>_exam.jsonl from the provided cache directory if they exist,
    logging the number of items loaded for each present file.
    
    Parameters:
        session_id (str): Session identifier used to locate cache files.
        cache_dir (Path): Directory containing cached JSONL files.
        logger (logging.Logger): Logger used to report load counts and warnings.
    
    Returns:
        dict: A dictionary with keys "transcript", "slides", and "exam", each mapped
        to a list of loaded items (empty list if the corresponding cache file is absent).
    """
    data = {
        "transcript": [],
        "slides": [],
        "exam": []
    }

    # Load transcript
    transcript_path = cache_dir / f"{session_id}_transcript.jsonl"
    if transcript_path.exists():
        data["transcript"] = read_jsonl(transcript_path)
        logger.info(f"Loaded {len(data['transcript'])} transcript segments")

    # Load slides
    slides_path = cache_dir / f"{session_id}_slides.jsonl"
    if slides_path.exists():
        data["slides"] = read_jsonl(slides_path)
        logger.info(f"Loaded {len(data['slides'])} slides")

    # Load exam
    exam_path = cache_dir / f"{session_id}_exam.jsonl"
    if exam_path.exists():
        data["exam"] = read_jsonl(exam_path)
        logger.info(f"Loaded {len(data['exam'])} exam questions")

    return data


def build_pipeline(
    config: ExamKitConfig,
    session_id: str,
    output_pdf_path: Path,
    logger: logging.Logger
) -> Dict[str, Any]:
    """
    Orchestrates the end-to-end generation of study materials (notes, citations, coverage, and optional PDF) for a given session.
    
    Parameters:
        config (ExamKitConfig): Configuration for embedding, retrieval, LLM, and output behavior.
        session_id (str): Identifier for the session whose processed data will be used.
        output_pdf_path (Path): Target path for the generated PDF output.
        logger (logging.Logger): Logger used for progress and error reporting.
    
    Returns:
        result (Dict[str, Any]): Summary of produced artifacts and metadata with keys:
            - "pdf_path": string path to the produced PDF file.
            - "notes_path": string path to the generated Markdown notes.
            - "citations_path": string path to the exported citations JSON.
            - "coverage_path": string path to the exported coverage CSV.
            - "topics_processed": number of topic sections that were produced.
            - "total_citations": total count of citations recorded by the CitationManager.
    
    Raises:
        ValueError: If no processed input chunks are found for the session (instructs to run ingestion first).
    """
    logger.info(f"Starting build pipeline for session: {session_id}")

    cache_dir = Path("cache")
    out_dir = output_pdf_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load processed data
    data = load_processed_data(session_id, cache_dir, logger)

    # Combine all chunks
    all_chunks = data["transcript"] + data["slides"] + data["exam"]
    if not all_chunks:
        raise ValueError("No processed data found. Run 'examkit ingest' first.")

    logger.info(f"Total chunks: {len(all_chunks)}")

    # Split into manageable chunks
    chunks = split_into_chunks(all_chunks, max_chunk_size=500, logger=logger)

    # Load embedding model
    logger.info("Loading embedding model...")
    model = load_embedding_model(config.embedding.model, logger)

    # Generate embeddings
    logger.info("Generating embeddings...")
    texts = [chunk.get("text", "") for chunk in chunks]
    embeddings = generate_embeddings(texts, model, config.embedding.batch_size, logger)

    # Create FAISS index
    logger.info("Creating FAISS index...")
    index = create_faiss_index(embeddings, config.embedding.dim, logger)

    # Save index
    index_path = cache_dir / f"{session_id}_index.faiss"
    metadata_path = cache_dir / f"{session_id}_metadata.pkl"
    save_index(index, index_path, chunks, metadata_path)

    # Load topics
    topics_path = Path("input/sample/topics/session_topics.yml")
    if not topics_path.exists():
        logger.warning("Topics file not found, using default topics")
        topics = [{"id": "default", "name": "Default Topic", "keywords": [], "weight": 1.0}]
    else:
        import yaml
        with open(topics_path, 'r') as f:
            topics_data = yaml.safe_load(f)
        topics = load_topics(topics_data.get("topics", []))

    logger.info(f"Loaded {len(topics)} topics")

    # Generate topic embeddings
    topic_texts = [f"{t['name']} {' '.join(t.get('keywords', []))}" for t in topics]
    topic_embeddings = generate_embeddings(topic_texts, model, config.embedding.batch_size, logger)

    # Map chunks to topics
    logger.info("Mapping chunks to topics...")
    topic_mapping = map_chunks_to_topics(chunks, topics, embeddings, topic_embeddings, logger=logger)

    # Calculate coverage
    coverage_data = calculate_coverage(topic_mapping, topics, len(chunks))

    # Initialize citation manager
    citation_mgr = CitationManager()

    # Generate content for each topic
    logger.info("Generating content with LLM...")
    sections = []

    for topic in topics:
        logger.info(f"Processing topic: {topic['name']}")

        # Retrieve relevant context
        context_chunks = retrieve_context_for_topic(
            topic, model, index, chunks,
            config.retrieval.top_k, logger
        )

        if not context_chunks:
            logger.warning(f"No context found for topic: {topic['name']}")
            continue

        # Generate sections
        section_content = {
            "topic": topic["name"],
            "definition": "",
            "key_formulas": "",
            "derivation": "",
            "examples": "",
            "mistakes": "",
            "revision": "",
            "citations": citation_mgr.format_multiple_citations(context_chunks)
        }

        # Definition
        try:
            def_prompt = render_definition_prompt(topic["name"], context_chunks[:3])
            section_content["definition"] = generate_completion(
                def_prompt,
                config.llm.model,
                config.llm.system_prompt,
                config.llm.temperature,
                config.llm.max_tokens,
                config.offline,
                logger
            )
        except Exception as e:
            logger.error(f"Failed to generate definition: {e}")

        # Derivation (if applicable)
        try:
            deriv_prompt = render_derivation_prompt(topic["name"], context_chunks[:5])
            section_content["derivation"] = generate_completion(
                deriv_prompt,
                config.llm.model,
                config.llm.system_prompt,
                config.llm.temperature,
                config.llm.max_tokens,
                config.offline,
                logger
            )
        except Exception as e:
            logger.error(f"Failed to generate derivation: {e}")

        # Common mistakes
        try:
            mistakes_prompt = render_mistakes_prompt(topic["name"], context_chunks)
            section_content["mistakes"] = generate_completion(
                mistakes_prompt,
                config.llm.model,
                config.llm.system_prompt,
                config.llm.temperature,
                config.llm.max_tokens,
                config.offline,
                logger
            )
        except Exception as e:
            logger.error(f"Failed to generate mistakes: {e}")

        # Quick revision
        try:
            revision_prompt = render_revision_prompt(topic["name"], context_chunks[:4])
            section_content["revision"] = generate_completion(
                revision_prompt,
                config.llm.model,
                config.llm.system_prompt,
                config.llm.temperature,
                config.llm.max_tokens,
                config.offline,
                logger
            )
        except Exception as e:
            logger.error(f"Failed to generate revision: {e}")

        sections.append(section_content)

    # Render to markdown
    logger.info("Rendering markdown...")
    markdown_content = render_markdown_document(sections, session_id, config)
    notes_path = out_dir / f"{session_id}_notes.md"
    write_text(markdown_content, notes_path)

    # Compile to PDF
    logger.info("Compiling PDF...")
    try:
        compile_typst_to_pdf(notes_path, output_pdf_path, config, logger)
    except Exception as e:
        logger.error(f"PDF compilation failed: {e}")
        logger.info("Markdown notes saved, but PDF generation failed")

    # Export citations
    citations_path = out_dir / f"{session_id}_citations.json"
    write_json(citation_mgr.export_citations(), citations_path)

    # Export coverage
    coverage_path = out_dir / f"{session_id}_coverage.csv"
    import pandas as pd
    df = pd.DataFrame(coverage_data)
    df.to_csv(coverage_path, index=False)

    logger.info("Build pipeline complete")

    return {
        "pdf_path": str(output_pdf_path),
        "notes_path": str(notes_path),
        "citations_path": str(citations_path),
        "coverage_path": str(coverage_path),
        "topics_processed": len(sections),
        "total_citations": citation_mgr.get_citation_count()
    }