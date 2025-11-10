"""
I/O utilities for file operations.
"""

import json
import shutil
from pathlib import Path
from typing import Any, Dict, List


def ensure_dir(path: Path) -> Path:
    """
    Ensure the directory at the given path exists, creating parent directories as needed.
    
    Parameters:
        path (Path): Directory path to ensure.
    
    Returns:
        Path: The same path that was provided.
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_json(path: Path) -> Dict[str, Any]:
    """
    Load and return the JSON object stored at the given file path.
    
    Returns:
        A dictionary representing the parsed JSON content of the file.
    """
    with open(path, "r") as f:
        return json.load(f)


def write_json(data: Dict[str, Any], path: Path, indent: int = 2) -> None:
    """
    Write a mapping to the given file as JSON, creating the parent directory if it does not exist.
    
    Parameters:
        data (Dict[str, Any]): Mapping to serialize to JSON.
        path (Path): Destination file path; the parent directory will be created if missing.
        indent (int): Number of spaces to use for JSON indentation.
    """
    ensure_dir(path.parent)
    with open(path, "w") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    """
    Load objects from a JSON Lines (JSONL) file, parsing each non-empty line as JSON.
    
    Parameters:
        path (Path): Path to the JSONL file to read.
    
    Returns:
        List[Dict[str, Any]]: A list of objects parsed from each non-empty line in the file.
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
    Write a list of dictionaries to a newline-delimited JSON (JSONL) file.
    
    Each dictionary is serialized as a single JSON object on its own line using UTF-8-compatible output (serialization uses `ensure_ascii=False`). The parent directory of `path` will be created if it does not exist.
    
    Parameters:
        data (List[Dict[str, Any]]): List of JSON-serializable dictionaries to write, one per line.
        path (Path): Destination file path for the JSONL output.
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
    Read the entire contents of a text file.
    
    Parameters:
        path (Path): Path to the text file.
        encoding (str): File encoding to use; defaults to "utf-8".
    
    Returns:
        str: The file contents.
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