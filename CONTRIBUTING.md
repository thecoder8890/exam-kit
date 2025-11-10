# Contributing to ExamKit

Thank you for your interest in contributing to ExamKit! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful, inclusive, and professional in all interactions.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/thecoder8890/exam-kit/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Your environment (OS, Python version, etc.)
   - Relevant logs or error messages

### Suggesting Enhancements

1. Check existing issues and discussions
2. Create an issue with:
   - Clear description of the enhancement
   - Use cases and benefits
   - Potential implementation approach

### Pull Requests

1. **Fork the repository**

2. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow existing code style
   - Add docstrings (Google style)
   - Include type hints
   - Write/update tests

4. **Test your changes**
   ```bash
   make test
   make lint
   ```

5. **Commit your changes**
   ```bash
   git commit -m "feat: add new feature"
   ```
   
   Use conventional commit messages:
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation
   - `test:` Tests
   - `refactor:` Code refactoring
   - `style:` Formatting
   - `chore:` Maintenance

6. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## Development Setup

### Prerequisites

- Python 3.11+
- Poetry
- System dependencies (see README)

### Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/exam-kit.git
cd exam-kit

# Install dependencies
make setup

# Run tests
make test
```

## Code Style

- **Python**: Follow PEP 8
- **Line length**: 100 characters
- **Formatting**: Use `black` (run `make format`)
- **Linting**: Use `ruff` (run `make lint`)
- **Type hints**: Use type hints for function signatures
- **Docstrings**: Google style docstrings for all public functions

### Example

```python
def process_transcript(
    path: Path,
    format: str = "vtt",
    logger: logging.Logger = None
) -> List[Dict[str, Any]]:
    """
    Process a transcript file.

    Args:
        path: Path to transcript file.
        format: Transcript format (vtt, srt, txt).
        logger: Optional logger instance.

    Returns:
        List of transcript segments.

    Raises:
        ValueError: If format is unsupported.
    """
    # Implementation
    pass
```

## Testing

- Write tests for new features
- Maintain or improve code coverage
- Run tests locally before submitting PR
- Tests should be in `tests/` directory
- Use pytest fixtures for setup/teardown

```python
def test_parse_vtt():
    """Test VTT parsing."""
    # Arrange
    content = "..."
    
    # Act
    result = parse_vtt(content)
    
    # Assert
    assert len(result) == 2
    assert result[0]["text"] == "Hello"
```

## Documentation

- Update README.md for user-facing changes
- Update docstrings for code changes
- Add examples for new features
- Update type hints

## Project Structure

Understand the architecture:

```
examkit/
├── cli.py          # CLI entry point
├── config.py       # Configuration models
├── ingestion/      # File parsing
├── nlp/            # NLP and embeddings
├── synthesis/      # LLM generation
├── render/         # PDF rendering
├── qa/             # Quality checks
└── reports/        # Reporting
```

## Questions?

- Open a [Discussion](https://github.com/thecoder8890/exam-kit/discussions)
- Ask in issues
- Check existing documentation

Thank you for contributing to ExamKit! 🎉
