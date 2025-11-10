"""
Pandoc renderer (fallback for PDF generation).
"""

import logging
import subprocess
from pathlib import Path
from typing import List, Optional


def render_markdown_to_pdf_pandoc(
    markdown_path: Path,
    output_pdf: Path,
    options: Optional[List[str]] = None,
    logger: logging.Logger = None
) -> bool:
    """
    Render a Markdown file to PDF using Pandoc.
    
    Parameters:
        markdown_path (Path): Path to the input Markdown file.
        output_pdf (Path): Path where the generated PDF will be written.
        options (Optional[List[str]]): Additional Pandoc command-line options to append.
        logger (logging.Logger, optional): Logger to receive informational and error messages.
    
    Returns:
        bool: `True` if Pandoc produced the PDF successfully, `False` otherwise.
    """
    if logger:
        logger.info(f"Rendering with Pandoc: {markdown_path} -> {output_pdf}")

    cmd = [
        "pandoc",
        str(markdown_path),
        "-o", str(output_pdf),
        "--pdf-engine=xelatex"
    ]

    if options:
        cmd.extend(options)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode == 0:
            if logger:
                logger.info(f"PDF generated: {output_pdf}")
            return True
        else:
            if logger:
                logger.error(f"Pandoc failed: {result.stderr}")
            return False

    except Exception as e:
        if logger:
            logger.error(f"Pandoc error: {e}")
        return False


def check_pandoc_installed() -> bool:
    """
    Determine whether Pandoc is available on the system PATH.
    
    Returns:
        True if running `pandoc --version` succeeds with exit code 0, False otherwise.
    """
    try:
        result = subprocess.run(
            ["pandoc", "--version"],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except:
        return False