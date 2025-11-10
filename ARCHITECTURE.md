# ExamKit Architecture

## Overview

ExamKit is a modular Python application that transforms lecture materials into exam-ready study notes. It follows a pipeline architecture with clear separation of concerns.

## System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                         Input Layer                          │
│  Video Files │ Transcripts │ Slides │ Exam Papers │ Topics   │
└──────────────────────────────────────────────────────────────┘
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                     Ingestion Module                         │
│  • FFmpeg audio extraction                                   │
│  • VTT/SRT/TXT transcript normalization                      │
│  • PPTX/PDF slides parsing                                   │
│  • Exam paper structure extraction                           │
│  • OCR with Tesseract                                        │
└──────────────────────────────────────────────────────────────┘
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                      Cache Layer                             │
│  JSONL files: transcript, slides, exam, manifest             │
└──────────────────────────────────────────────────────────────┘
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                       NLP Module                             │
│  • Text chunking and segmentation                            │
│  • Embeddings (sentence-transformers)                        │
│  • FAISS vector index                                        │
│  • Topic mapping                                             │
│  • Coverage calculation                                      │
└──────────────────────────────────────────────────────────────┘
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    Synthesis Module                          │
│  • RAG retrieval (top-k chunks per topic)                    │
│  • Prompt templating (Jinja2)                                │
│  • LLM generation (Ollama)                                   │
│  • Citation management                                       │
│  • Diagram generation (Graphviz)                             │
└──────────────────────────────────────────────────────────────┘
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                     Render Module                            │
│  • Markdown compilation                                      │
│  • Typst/Pandoc PDF generation                               │
│  • Template processing                                       │
└──────────────────────────────────────────────────────────────┘
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    QA & Reports Module                       │
│  • Formula validation                                        │
│  • Link checking                                             │
│  • Coverage reports                                          │
│  • Citation export                                           │
└──────────────────────────────────────────────────────────────┘
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                       Output Layer                           │
│  PDF │ Markdown │ Citations JSON │ Coverage CSV              │
└──────────────────────────────────────────────────────────────┘
```

## Module Descriptions

### 1. CLI Module (`cli.py`)

**Purpose**: Command-line interface using Typer

**Commands**:
- `ingest`: Process input files
- `build`: Generate study notes
- `report`: Display coverage and QA
- `cache clear`: Clean cached data

**Dependencies**: Typer, Rich

### 2. Configuration (`config.py`)

**Purpose**: Configuration management with Pydantic models

**Key Components**:
- `ExamKitConfig`: Main configuration
- Sub-configs: ASR, LLM, Embedding, Retrieval, PDF, Diagrams

**Format**: YAML with type validation

### 3. Ingestion Module

**Purpose**: Parse and normalize input files

**Components**:
- `ingest.py`: Main pipeline coordinator
- `transcript_normalizer.py`: VTT/SRT/TXT → JSONL
- `slides_parser.py`: PPTX/PDF extraction
- `exam_parser.py`: Question structure parsing
- `ocr.py`: Tesseract wrapper

**Output**: Normalized JSONL files in cache

### 4. ASR Module

**Purpose**: Audio transcription

**Component**:
- `whisper_runner.py`: faster-whisper wrapper

**Features**:
- Offline processing
- Multiple model sizes
- VAD support
- VTT export

### 5. NLP Module

**Purpose**: Natural language processing and semantic analysis

**Components**:
- `splitter.py`: Text segmentation
- `embeddings.py`: sentence-transformers + FAISS
- `topic_mapping.py`: Map chunks to topics
- `retrieval.py`: RAG retrieval
- `spacy_nlp.py`: NER and text analysis

**Key Operations**:
- Generate embeddings (384-dim)
- Create FAISS index
- Calculate topic coverage
- Retrieve relevant context

### 6. Synthesis Module

**Purpose**: Content generation using LLM

**Components**:
- `ollama_client.py`: Ollama API wrapper
- `prompts.py`: Jinja2 prompt templates
- `composer.py`: Main synthesis pipeline
- `citations.py`: Citation tracking
- `diagrams.py`: Graphviz diagram generation

**Prompt Types**:
- Definition
- Derivation
- Common mistakes
- Quick revision
- Worked examples

### 7. Render Module

**Purpose**: PDF generation

**Components**:
- `templater.py`: Jinja2 template rendering
- `typst_renderer.py`: Typst compilation (preferred)
- `pandoc_renderer.py`: Pandoc fallback

**Output**: PDF with ToC, citations, formulas

### 8. QA Module

**Purpose**: Quality assurance checks

**Component**:
- `checks.py`: Validation functions

**Checks**:
- LaTeX formula syntax
- Internal link validity
- Keyword coverage
- Citation presence

### 9. Reports Module

**Purpose**: Generate coverage and analysis reports

**Components**:
- `coverage.py`: Topic coverage metrics
- `export.py`: Report export (JSON, CSV, TXT)

## Data Flow

### 1. Ingestion Phase

```python
Manifest → validate_manifest()
Video → ffmpeg → WAV (16kHz mono)
Transcript (VTT/SRT/TXT) → normalize_transcript() → JSONL
Slides (PPTX/PDF) → parse_slides() → JSONL (+ OCR if needed)
Exam (PDF) → parse_exam() → JSONL
```

### 2. Processing Phase

```python
Load JSONL files
Split into chunks (max 500 chars)
Generate embeddings (all-MiniLM-L6-v2)
Create FAISS index
Map chunks to topics
```

### 3. Synthesis Phase

```python
For each topic:
  1. Retrieve top-k relevant chunks
  2. Format prompt with context
  3. Generate with Ollama
  4. Track citations
  5. Collect sections
```

### 4. Rendering Phase

```python
Sections → render_markdown_document()
Markdown → Typst/Pandoc
Typst → PDF
Save citations, coverage
```

## Key Design Decisions

### 1. Offline-First

- No external APIs (except local Ollama)
- All models run locally
- Reproducible builds

### 2. Modular Architecture

- Clear separation of concerns
- Each module can be tested independently
- Easy to extend or replace components

### 3. Citation Tracking

- Every generated paragraph cites sources
- Multiple citation types (video, slide, exam)
- Maintains traceability

### 4. Configurable Pipeline

- YAML configuration
- Multiple rendering backends
- Adjustable model parameters

### 5. Type Safety

- Pydantic models for config
- Type hints throughout
- Validation at boundaries

## Performance Considerations

### Bottlenecks

1. **Embedding Generation**: O(n × batch_size)
   - Solution: Adjust batch_size in config
   - Cache embeddings for reuse

2. **LLM Generation**: ~1-5 seconds per prompt
   - Solution: Parallel processing possible
   - Use smaller model for speed

3. **FAISS Search**: O(log n) but memory intensive
   - Solution: Use quantization if needed

### Optimization Strategies

1. **Caching**: Store processed data in cache/
2. **Batch Processing**: Process embeddings in batches
3. **Lazy Loading**: Load models only when needed
4. **Parallel Processing**: Can parallelize topic processing

## Extension Points

### Adding New Input Format

1. Create parser in `ingestion/`
2. Output to JSONL format
3. Update `ingest.py` to call parser

### Adding New LLM Backend

1. Create client in `synthesis/`
2. Implement `generate_completion()` interface
3. Update config to support new engine

### Adding New Renderer

1. Create renderer in `render/`
2. Implement compilation function
3. Add to `typst_renderer.py` dispatch

### Custom Prompt Templates

1. Add `.j2` template to `config/templates/prompts/`
2. Add render function in `prompts.py`
3. Use in `composer.py`

## Testing Strategy

### Unit Tests

- Test individual functions
- Mock external dependencies
- Use fixtures for sample data

### Integration Tests

- Test module interactions
- Use sample data in `input/sample/`
- Verify output formats

### End-to-End Tests

- Run full pipeline
- Check PDF generation
- Validate coverage metrics

## Security Considerations

1. **No Network Calls**: Enforced by offline flag
2. **Input Validation**: Manifest and file checks
3. **Sandboxed Execution**: No arbitrary code execution
4. **Safe LaTeX**: Formula validation before rendering

## Future Enhancements

1. **Web UI**: Flask/FastAPI interface
2. **Incremental Updates**: Update only changed topics
3. **Multi-language**: Support non-English content
4. **Cloud Sync**: Optional cloud storage
5. **Collaborative**: Multi-user editing
6. **Mobile**: React Native app

## Dependencies

### Core

- **Python 3.11+**: Language runtime
- **Typer**: CLI framework
- **Pydantic**: Config validation
- **Rich**: Terminal output

### NLP/ML

- **sentence-transformers**: Embeddings
- **faiss-cpu**: Vector search
- **spacy**: NLP
- **faster-whisper**: ASR

### Document Processing

- **PyMuPDF**: PDF parsing
- **python-pptx**: PPTX parsing
- **pytesseract**: OCR

### LLM

- **Ollama**: Local LLM server
- **requests**: HTTP client

### Rendering

- **Jinja2**: Templating
- **Typst** (external): PDF compilation
- **Pandoc** (external): Fallback renderer

### System

- **ffmpeg** (external): Audio extraction
- **tesseract** (external): OCR engine
- **graphviz**: Diagrams

## Deployment

### Development

```bash
poetry install
make setup
poetry run examkit --help
```

### Production

1. Install system dependencies
2. Install Python package
3. Configure via config.yml
4. Run with appropriate resources

### Docker (Future)

Could be containerized with all dependencies pre-installed.

## Monitoring

### Logging

- Console: Rich formatting
- File: Structured logs in `logs/`
- Levels: DEBUG, INFO, WARNING, ERROR

### Metrics

- Processing time per stage
- Token counts for LLM
- Coverage percentages
- QA check results

## Troubleshooting

See README.md for common issues and solutions.

---

**Last Updated**: 2024-11-09
