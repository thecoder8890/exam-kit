"""
Logging utilities for ExamKit.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler

console = Console()


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    rich_output: bool = True
) -> logging.Logger:
    """
    Configure and return the "examkit" logger with console and optional file handlers.
    
    Parameters:
        level (str): Logging level name (e.g., "DEBUG", "INFO"). Invalid or unknown names default to "INFO".
        log_file (Optional[Path]): If provided, a file handler is added and the file's parent directory will be created if necessary.
        rich_output (bool): If True, console output is formatted with Rich; otherwise a standard stream formatter is used.
    
    Returns:
        logging.Logger: The configured logger named "examkit".
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Create logger
    logger = logging.getLogger("examkit")
    logger.setLevel(numeric_level)

    # Remove existing handlers
    logger.handlers.clear()

    # Console handler
    if rich_output:
        console_handler = RichHandler(
            console=console,
            rich_tracebacks=True,
            show_time=True,
            show_path=True
        )
    else:
        console_handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(formatter)

    console_handler.setLevel(numeric_level)
    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Retrieve a namespaced logger for the given module.
    
    Parameters:
        name (str): Module name to namespace under "examkit".
    
    Returns:
        logging.Logger: Logger named "examkit.<name>".
    """
    return logging.getLogger(f"examkit.{name}")