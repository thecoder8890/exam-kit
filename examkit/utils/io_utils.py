"""
I/O utilities for file operations.
"""

import json
import shutil
from pathlib import Path
from typing import Any, Dict, List


def ensure_dir(path: Path) -> Path:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path to ensure.

    Returns:
        The directory path.
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_json(path: Path) -> Dict[str, Any]:
    """
    Read and parse a JSON file.

    Args:
        path: Path to JSON file.

    Returns:
        Parsed JSON data as dictionary.
    """
    with open(path, "r") as f:
        return json.load(f)


def write_json(data: Dict[str, Any], path: Path, indent: int = 2) -> None:
    """
    Write data to a JSON file.

    Args:
        data: Data to write.
        path: Output path.
        indent: JSON indentation level.
    """
    ensure_dir(path.parent)
    with open(path, "w") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    """
    Read a JSONL (JSON Lines) file.

    Args:
        path: Path to JSONL file.

    Returns:
        List of dictionaries, one per line.
    """
    data = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                data.append(json.loads(line))
    return data


def write_jsonl(data: List[Dict[str, Any]], path: Path) -> None:
    """
    Write data to a JSONL file.

    Args:
        data: List of dictionaries to write.
        path: Output path.
    """
    ensure_dir(path.parent)
    with open(path, "w") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


def copy_file(src: Path, dst: Path) -> None:
    """
    Copy a file from source to destination.

    Args:
        src: Source file path.
        dst: Destination file path.
    """
    ensure_dir(dst.parent)
    shutil.copy2(src, dst)


def read_text(path: Path, encoding: str = "utf-8") -> str:
    """
    Read text file contents.

    Args:
        path: Path to text file.
        encoding: Text encoding.

    Returns:
        File contents as string.
    """
    with open(path, "r", encoding=encoding) as f:
        return f.read()


def write_text(content: str, path: Path, encoding: str = "utf-8") -> None:
    """
    Write text content to a file.

    Args:
        content: Text content to write.
        path: Output path.
        encoding: Text encoding.
    """
    ensure_dir(path.parent)
    with open(path, "w", encoding=encoding) as f:
        f.write(content)
