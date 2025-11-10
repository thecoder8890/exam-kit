"""
Template rendering for markdown and Typst documents.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from jinja2 import Environment, FileSystemLoader, Template

from examkit.config import ExamKitConfig


def setup_jinja_environment(templates_dir: Path = None) -> Environment:
    """
    Create a Jinja2 Environment configured to load templates from a filesystem directory.
    
    Parameters:
        templates_dir (Path | None): Path to the templates directory. If omitted, defaults to "config/templates".
    
    Returns:
        Environment: A Jinja2 Environment with FileSystemLoader and `trim_blocks` and `lstrip_blocks` enabled.
    """
    if templates_dir is None:
        templates_dir = Path("config/templates")

    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        trim_blocks=True,
        lstrip_blocks=True
    )

    return env


def render_markdown_document(
    sections: List[Dict[str, Any]],
    session_id: str,
    config: ExamKitConfig
) -> str:
    """
    Builds a complete Markdown document from structured section data for an exam preparation session.
    
    Parameters:
        sections (List[Dict[str, Any]]): Ordered list of section dictionaries. Each section may include keys:
            - "topic" (str): section title.
            - "definition" (str): definition text.
            - "key_formulas" (str): key formulas text.
            - "derivation" (str): derivation text.
            - "examples" (str): worked examples text.
            - "mistakes" (str): common mistakes text.
            - "revision" (str): quick revision notes.
            - "citations" (str): optional sources to display with a definition.
        session_id (str): Identifier to include in the document title.
        config (ExamKitConfig): Configuration object (used for environment/context; not directly inspected by this function).
    
    Returns:
        str: The rendered Markdown document as a single string.
    """
    # Build markdown manually (simple template)
    lines = [
        f"# Exam Preparation Notes - {session_id}",
        f"",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"",
        f"---",
        f""
    ]

    # Table of contents
    lines.append("## Table of Contents\n")
    for i, section in enumerate(sections, 1):
        topic = section.get("topic", f"Topic {i}")
        lines.append(f"{i}. [{topic}](#{topic.lower().replace(' ', '-')})")
    lines.append("\n---\n")

    # Sections
    for i, section in enumerate(sections, 1):
        topic = section.get("topic", f"Topic {i}")
        citations = section.get("citations", "")

        lines.append(f"## {i}. {topic}\n")

        if section.get("definition"):
            lines.append(f"### Definition\n")
            lines.append(f"{section['definition']}\n")
            if citations:
                lines.append(f"*Sources: {citations}*\n")

        if section.get("key_formulas"):
            lines.append(f"### Key Formulas\n")
            lines.append(f"{section['key_formulas']}\n")

        if section.get("derivation"):
            lines.append(f"### Derivation\n")
            lines.append(f"{section['derivation']}\n")

        if section.get("examples"):
            lines.append(f"### Worked Examples\n")
            lines.append(f"{section['examples']}\n")

        if section.get("mistakes"):
            lines.append(f"### Common Mistakes\n")
            lines.append(f"{section['mistakes']}\n")

        if section.get("revision"):
            lines.append(f"### Quick Revision\n")
            lines.append(f"{section['revision']}\n")

        lines.append("\n---\n")

    return "\n".join(lines)


def render_typst_document(
    markdown_content: str,
    session_id: str,
    config: ExamKitConfig
) -> str:
    """
    Render a Typst document from rendered Markdown content.
    
    Builds a Typst preface (theme import and conf block with title and date) and converts common Markdown constructs (headers and simple emphasis) into Typst syntax, producing a complete Typst document.
    
    Parameters:
        markdown_content (str): Markdown text to convert.
        session_id (str): Session identifier inserted into the document title.
        config (ExamKitConfig): Configuration used for rendering (controls template/formatting options).
    
    Returns:
        str: The complete Typst document content.
    """
    # Convert markdown to Typst format (basic conversion)
    typst_lines = [
        "#import \"theme.typ\": *",
        "",
        f"#show: doc => conf(",
        f"  title: \"Exam Notes - {session_id}\",",
        f"  date: datetime.today().display(),",
        f"  doc",
        ")",
        ""
    ]

    # Simple markdown to Typst conversion
    for line in markdown_content.split('\n'):
        # Headers
        if line.startswith('### '):
            typst_lines.append(f"=== {line[4:]}")
        elif line.startswith('## '):
            typst_lines.append(f"== {line[3:]}")
        elif line.startswith('# '):
            typst_lines.append(f"= {line[2:]}")
        # Bold
        elif '**' in line:
            line = line.replace('**', '*')
            typst_lines.append(line)
        # Italic (markdown style)
        elif line.startswith('*') and line.endswith('*') and '**' not in line:
            typst_lines.append(f"_{line[1:-1]}_")
        else:
            typst_lines.append(line)

    return "\n".join(typst_lines)


def load_template(template_name: str, templates_dir: Path = None) -> Template:
    """
    Load a Jinja2 template from the templates directory.
    
    Parameters:
        template_name (str): Name of the template file to load.
        templates_dir (Path | None): Optional path to the templates directory; when omitted the configured templates directory is used.
    
    Returns:
        template (Template): The loaded Jinja2 Template object.
    """
    env = setup_jinja_environment(templates_dir)
    return env.get_template(template_name)


def render_section_template(
    template_name: str,
    context: Dict[str, Any],
    templates_dir: Path = None
) -> str:
    """
    Render a section template.

    Args:
        template_name: Template file name.
        context: Template context variables.
        templates_dir: Templates directory.

    Returns:
        Rendered content.
    """
    template = load_template(template_name, templates_dir)
    return template.render(**context)