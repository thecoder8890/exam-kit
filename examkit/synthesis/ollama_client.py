"""
Ollama LLM client for local inference.
"""

import json
import logging
import subprocess
from typing import Any, Dict, Optional

import requests


def check_ollama_available() -> bool:
    """
    Check if Ollama is available.

    Returns:
        True if available, False otherwise.
    """
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False


def list_models() -> list:
    """
    List available Ollama models.

    Returns:
        List of model names.
    """
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
    except:
        pass
    return []


def generate_completion(
    prompt: str,
    model: str = "llama3.2:8b",
    system_prompt: Optional[str] = None,
    temperature: float = 0.2,
    max_tokens: int = 900,
    offline: bool = True,
    logger: logging.Logger = None
) -> str:
    """
    Generate completion using Ollama.

    Args:
        prompt: User prompt.
        model: Model name.
        system_prompt: System prompt.
        temperature: Sampling temperature.
        max_tokens: Maximum tokens to generate.
        offline: Enforce offline mode.
        logger: Logger instance.

    Returns:
        Generated text.
    """
    if offline and not check_ollama_available():
        raise RuntimeError("Ollama not available. Start with: ollama serve")

    if logger:
        logger.debug(f"Generating completion with model: {model}")

    # Prepare request
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens
        }
    }

    if system_prompt:
        payload["system"] = system_prompt

    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()

        result = response.json()
        generated_text = result.get("response", "")

        if logger:
            logger.debug(f"Generated {len(generated_text)} characters")

        return generated_text

    except requests.exceptions.RequestException as e:
        if logger:
            logger.error(f"Ollama request failed: {e}")
        raise RuntimeError(f"Failed to generate completion: {e}")


def generate_chat_completion(
    messages: list,
    model: str = "llama3.2:8b",
    temperature: float = 0.2,
    max_tokens: int = 900,
    logger: logging.Logger = None
) -> str:
    """
    Generate chat completion using Ollama.

    Args:
        messages: List of message dicts with 'role' and 'content'.
        model: Model name.
        temperature: Sampling temperature.
        max_tokens: Maximum tokens to generate.
        logger: Logger instance.

    Returns:
        Generated response.
    """
    if not check_ollama_available():
        raise RuntimeError("Ollama not available")

    url = "http://localhost:11434/api/chat"
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens
        }
    }

    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()

        result = response.json()
        message = result.get("message", {})
        return message.get("content", "")

    except requests.exceptions.RequestException as e:
        if logger:
            logger.error(f"Ollama chat request failed: {e}")
        raise RuntimeError(f"Failed to generate chat completion: {e}")


def pull_model(model: str, logger: logging.Logger = None) -> bool:
    """
    Pull a model using Ollama CLI.

    Args:
        model: Model name to pull.
        logger: Logger instance.

    Returns:
        True if successful, False otherwise.
    """
    if logger:
        logger.info(f"Pulling Ollama model: {model}")

    try:
        result = subprocess.run(
            ["ollama", "pull", model],
            capture_output=True,
            text=True,
            timeout=600
        )
        return result.returncode == 0
    except Exception as e:
        if logger:
            logger.error(f"Failed to pull model: {e}")
        return False
