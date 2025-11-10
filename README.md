# ExamKit

**Production-grade exam preparation toolkit for macOS - Offline, Local-Only Processing**

ExamKit is a comprehensive Python application that transforms lecture materials (videos, transcripts, slides, exam papers) into exam-ready study notes with citations, formulas, and coverage reports.

## ✨ Features

- 🎥 **Multi-Source Ingestion**: Process videos, transcripts (VTT/SRT), slides (PPTX/PDF), and exam papers
- 🗣️ **Offline ASR**: Transcribe audio using faster-whisper (no cloud APIs)
- 🧠 **Local LLM**: Generate content using Ollama (llama3.2:8b) running locally
- 📊 **RAG Pipeline**: Semantic search with sentence-transformers and FAISS
- 📖 **Structured Output**: Generate PDF study notes with definitions, derivations, examples, and common mistakes
- 🔍 **Citation Tracking**: Every paragraph cites sources (video timecodes, slide numbers, exam questions)
- 📈 **Coverage Analysis**: Track which topics are covered by your materials
- ✅ **Quality Assurance**: Automated checks for formulas, links, and citations
- 🎨 **Beautiful PDFs**: Typst or Pandoc rendering with customizable themes

## 🏗️ Architecture

```
┌─────────────────┐
│  Input Sources  │
│ Video, Slides,  │
│ Transcripts,    │
│ Exam Papers     │
└────────┬────────┘
         │
         v
┌─────────────────┐
│   Ingestion     │
│ - FFmpeg Audio  │
│ - OCR (Tesseract)│
│ - Text Parsing  │
└────────┬────────┘
         │
         v
┌─────────────────┐
│   NLP Pipeline  │
│ - Chunking      │
│ - Embeddings    │
│ - FAISS Index   │
│ - Topic Mapping │
└────────┬────────┘
         │
         v
┌─────────────────┐
│   Synthesis     │
│ - RAG Retrieval │
│ - LLM (Ollama)  │
│ - Citations     │
│ - Diagrams      │
└────────┬────────┘
         │
         v
┌─────────────────┐
│   Rendering     │
│ - Markdown      │
│ - Typst/Pandoc  │
│ - PDF Output    │
└────────┬────────┘
         │
         v
┌─────────────────┐
│    Outputs      │
│ PDF, Citations, │
│ Coverage Report │
└─────────────────┘
```

## 📋 Prerequisites

### System Requirements

- **macOS** (Apple Silicon or Intel)
- **Python 3.11+**
- **Homebrew** (for system dependencies)

### System Dependencies

Install via Homebrew:

```bash
# Core tools
brew install ffmpeg tesseract graphviz typst

# Ollama (for local LLM)
brew install ollama

# Start Ollama service
ollama serve &

# Pull the default model
ollama pull llama3.2:8b
```

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/thecoder8890/exam-kit.git
cd exam-kit
```

### 2. Set Up Python Environment

Using Poetry (recommended):

```bash
# Install Poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Download spaCy model
poetry run python -m spacy download en_core_web_sm
```

Using pip:

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e .

# Download spaCy model
python -m spacy download en_core_web_sm
```

### 3. Verify Installation

```bash
# Using Make
make install-system-deps  # See installation instructions
make setup                # Install Python deps

# Test the CLI
poetry run examkit --help
```

## 📖 Usage

### Quick Start

```bash
# 1. Prepare your manifest (see input/sample/manifest.json)
# 2. Ingest and preprocess materials
poetry run examkit ingest --manifest input/sample/manifest.json

# 3. Build exam notes
poetry run examkit build --config config/config.yml --out out/exam_notes.pdf --offline

# 4. View coverage report
poetry run examkit report --session demo --open
```

### CLI Commands

#### `examkit ingest`

Process input files and prepare them for synthesis.

```bash
poetry run examkit ingest \
  --manifest path/to/manifest.json \
  --cache cache/ \
  --log-level INFO
```

**Manifest Format:**

```json
{
  "session_id": "lec05",
  "course": "Computer Science 101",
  "inputs": {
    "video": "input/lecture05.mp4",
    "transcript": "input/lecture05.vtt",
    "slides": "input/slides05.pptx",
    "exam": "input/exam_2024.pdf",
    "topics": "input/topics.yml"
  }
}
```

#### `examkit build`

Generate exam-ready PDF from processed inputs.

```bash
poetry run examkit build \
  --config config/config.yml \
  --out out/lecture05.pdf \
  --session lec05 \
  --offline
```

#### `examkit report`

Generate coverage and QA report.

```bash
poetry run examkit report \
  --session lec05 \
  --open  # Open coverage CSV after generation
```

#### `examkit cache clear`

Clear cached files.

```bash
poetry run examkit cache clear
```

## ⚙️ Configuration

Edit `config/config.yml` to customize behavior:

```yaml
asr:
  engine: faster-whisper
  model: small  # tiny, base, small, medium, large
  language: en
  vad: true

llm:
  engine: ollama
  model: llama3.2:8b
  temperature: 0.2
  max_tokens: 900
  system_prompt: "You create exam-ready, cited study notes..."

embedding:
  model: all-MiniLM-L6-v2
  dim: 384
  batch_size: 32

retrieval:
  top_k: 8
  max_context_tokens: 2000

pdf:
  engine: typst  # or pandoc
  theme: classic
  font_size: 11
  include_appendix: true

offline: true
```

## 📁 Project Structure

```
examkit/
├── examkit/              # Main package
│   ├── cli.py           # Typer CLI
│   ├── config.py        # Pydantic config models
│   ├── utils/           # Utilities (I/O, text, math, timecode)
│   ├── ingestion/       # File parsing (video, slides, exam)
│   ├── asr/             # Audio transcription (faster-whisper)
│   ├── nlp/             # NLP (embeddings, RAG, topic mapping)
│   ├── synthesis/       # LLM generation (Ollama)
│   ├── render/          # PDF rendering (Typst/Pandoc)
│   ├── qa/              # Quality checks
│   └── reports/         # Coverage and export
├── config/              # Configuration and templates
│   ├── config.yml
│   └── templates/
│       ├── typst/       # Typst templates
│       ├── markdown/    # Markdown templates
│       └── prompts/     # LLM prompts
├── input/               # Input files
│   └── sample/          # Sample data for testing
├── tests/               # pytest tests
├── pyproject.toml       # Poetry dependencies
├── Makefile             # Build automation
└── README.md
```

## 🧪 Testing

Run tests with pytest:

```bash
# Run all tests
make test

# Or directly with poetry
poetry run pytest -v

# With coverage
poetry run pytest --cov=examkit --cov-report=html
```

## 🔧 Development

### Code Quality

```bash
# Format code
make format

# Lint code
make lint

# Type checking (if configured)
poetry run mypy examkit/
```

### Building Demo

```bash
make build-demo
```

## 🐛 Troubleshooting

### Common Issues

**1. Typst Not Found**

```bash
# Install Typst
brew install typst

# Verify installation
typst --version
```

**2. Ollama Not Running**

```bash
# Start Ollama service
ollama serve &

# Check if model is available
ollama list

# Pull model if missing
ollama pull llama3.2:8b
```

**3. spaCy Model Missing**

```bash
poetry run python -m spacy download en_core_web_sm
```

**4. OCR Confidence Low**

- Increase image resolution in slides parser
- Use `--model medium` or `--model large` for faster-whisper
- Preprocess images with higher DPI

**5. Memory Issues**

- Reduce `embedding.batch_size` in config
- Use smaller Whisper model (tiny, base)
- Process fewer chunks at a time

## 📝 License

MIT License - see [LICENSE](LICENSE) file.

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run `make test` and `make lint`
5. Submit a pull request

## 📚 Citation

If you use ExamKit in your research or project, please cite:

```bibtex
@software{examkit2024,
  title = {ExamKit: Production-Grade Exam Preparation Toolkit},
  author = {ExamKit Contributors},
  year = {2024},
  url = {https://github.com/thecoder8890/exam-kit}
}
```

## 🙏 Acknowledgments

Built with:
- [faster-whisper](https://github.com/guillaumekln/faster-whisper)
- [Ollama](https://ollama.ai/)
- [sentence-transformers](https://www.sbert.net/)
- [FAISS](https://github.com/facebookresearch/faiss)
- [Typst](https://typst.app/)
- [Typer](https://typer.tiangolo.com/)
- [Rich](https://rich.readthedocs.io/)

---

**Made with ❤️ for students preparing for exams**