"""
Typst rendering for PDF generation.
"""

import logging
import subprocess
from pathlib import Path

from examkit.config import ExamKitConfig
from examkit.utils.io_utils import write_text


def check_typst_installed() -> bool:
    """
    Check if Typst is installed.

    Returns:
        True if installed, False otherwise.
    """
    try:
        result = subprocess.run(
            ["typst", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def compile_typst_to_pdf(
    input_path: Path,
    output_path: Path,
    config: ExamKitConfig,
    logger: logging.Logger
) -> bool:
    """
    Compile Typst/Markdown to PDF.

    Args:
        input_path: Path to input file (markdown or typst).
        output_path: Path for output PDF.
        config: Configuration.
        logger: Logger instance.

    Returns:
        True if successful, False otherwise.
    """
    if config.pdf.engine == "typst":
        return compile_with_typst(input_path, output_path, logger)
    elif config.pdf.engine == "pandoc":
        return compile_with_pandoc(input_path, output_path, config, logger)
    else:
        logger.error(f"Unknown PDF engine: {config.pdf.engine}")
        return False


def compile_with_typst(
    input_path: Path,
    output_path: Path,
    logger: logging.Logger
) -> bool:
    """
    Compile using Typst.

    Args:
        input_path: Input file path.
        output_path: Output PDF path.
        logger: Logger instance.

    Returns:
        True if successful, False otherwise.
    """
    if not check_typst_installed():
        logger.error("Typst not installed. Install with: brew install typst")
        return False

    logger.info(f"Compiling with Typst: {input_path} -> {output_path}")

    # Create a simple Typst wrapper if input is markdown
    if input_path.suffix == '.md':
        typst_content = create_typst_wrapper_for_markdown(input_path)
        typst_path = input_path.with_suffix('.typ')
        write_text(typst_content, typst_path)
        input_path = typst_path

    try:
        result = subprocess.run(
            ["typst", "compile", str(input_path), str(output_path)],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            logger.info(f"PDF generated successfully: {output_path}")
            return True
        else:
            logger.error(f"Typst compilation failed: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        logger.error("Typst compilation timed out")
        return False
    except Exception as e:
        logger.error(f"Typst compilation error: {e}")
        return False


def create_typst_wrapper_for_markdown(markdown_path: Path) -> str:
    """
    Create a Typst wrapper that includes markdown content.

    Args:
        markdown_path: Path to markdown file.

    Returns:
        Typst content.
    """
    with open(markdown_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Basic markdown to Typst conversion
    typst_lines = [
        "// Auto-generated Typst document",
        "",
        "#set page(paper: \"a4\", margin: 1in)",
        "#set text(size: 11pt)",
        "#set par(justify: true, leading: 0.65em)",
        "#set heading(numbering: \"1.1\")",
        "",
        "// Document content",
        ""
    ]

    # Convert markdown headings to Typst
    for line in md_content.split('\n'):
        if line.startswith('### '):
            typst_lines.append(f"=== {line[4:]}")
        elif line.startswith('## '):
            typst_lines.append(f"== {line[3:]}")
        elif line.startswith('# '):
            typst_lines.append(f"= {line[2:]}")
        else:
            # Basic text conversion
            line = line.replace('**', '*')  # Bold
            line = line.replace('`', '```')  # Code
            typst_lines.append(line)

    return "\n".join(typst_lines)


def compile_with_pandoc(
    input_path: Path,
    output_path: Path,
    config: ExamKitConfig,
    logger: logging.Logger
) -> bool:
    """
    Compile using Pandoc (fallback).

    Args:
        input_path: Input markdown file.
        output_path: Output PDF path.
        config: Configuration.
        logger: Logger instance.

    Returns:
        True if successful, False otherwise.
    """
    logger.info(f"Compiling with Pandoc: {input_path} -> {output_path}")

    try:
        # Check if pandoc is available
        subprocess.run(["pandoc", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("Pandoc not installed. Install with: brew install pandoc")
        return False

    try:
        result = subprocess.run(
            [
                "pandoc",
                str(input_path),
                "-o", str(output_path),
                "--pdf-engine=xelatex",
                "-V", "geometry:margin=1in",
                "-V", f"fontsize={config.pdf.font_size}pt",
                "--toc",
                "--number-sections"
            ],
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode == 0:
            logger.info(f"PDF generated successfully: {output_path}")
            return True
        else:
            logger.error(f"Pandoc compilation failed: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        logger.error("Pandoc compilation timed out")
        return False
    except Exception as e:
        logger.error(f"Pandoc compilation error: {e}")
        return False
