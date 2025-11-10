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
    Render markdown to PDF using Pandoc.

    Args:
        markdown_path: Path to markdown file.
        output_pdf: Path for output PDF.
        options: Additional Pandoc options.
        logger: Logger instance.

    Returns:
        True if successful, False otherwise.
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
    Check if Pandoc is installed.

    Returns:
        True if installed, False otherwise.
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
