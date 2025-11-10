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
    Determine whether a local Ollama HTTP service is reachable.
    
    Performs a short HTTP GET to the local /api/tags endpoint and treats an HTTP 200 response as available.
    
    Returns:
        `True` if the local Ollama service responds with HTTP 200, `False` otherwise.
    """
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False


def list_models() -> list:
    """
    Retrieve names of models available from the local Ollama API.
    
    Returns:
        list: Model name strings. Returns an empty list if the Ollama API is unreachable or does not return a 200 response.
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
    Generate a text completion from a local Ollama model.
    
    Parameters:
        prompt (str): The user prompt to send to the model.
        system_prompt (Optional[str]): Optional system-level prompt to guide generation.
        temperature (float): Sampling temperature controlling randomness; higher values increase randomness.
        max_tokens (int): Maximum number of tokens to generate.
        offline (bool): If True, require a local Ollama server to be available before attempting generation.
    
    Returns:
        str: The generated text produced by the model.
    
    Raises:
        RuntimeError: If offline is True and the local Ollama server is unavailable, or if the HTTP request to Ollama fails.
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
    Generate a chat response from the local Ollama model for a sequence of messages.
    
    Parameters:
        messages (list): List of message dictionaries each containing 'role' (e.g., 'user'|'assistant'|'system') and 'content' (str).
        model (str): Ollama model identifier to use.
        temperature (float): Sampling temperature for response generation.
        max_tokens (int): Maximum number of tokens to generate.
        logger (logging.Logger, optional): Logger for error/debug messages (not required).
    
    Returns:
        str: The generated message content (empty string if none present).
    
    Raises:
        RuntimeError: If Ollama is not available or the HTTP request to Ollama fails.
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
    Pull the specified Ollama model via the local Ollama CLI.
    
    Parameters:
        model (str): Name of the model to pull.
    
    Returns:
        True if the CLI reported success (exit code 0), False otherwise.
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