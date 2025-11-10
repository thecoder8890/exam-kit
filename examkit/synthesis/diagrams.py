"""
Diagram generation utilities using Graphviz.
"""

import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import graphviz
    GRAPHVIZ_AVAILABLE = True
except ImportError:
    GRAPHVIZ_AVAILABLE = False


def create_flowchart(
    nodes: List[Dict[str, str]],
    edges: List[tuple],
    title: str = "Flowchart",
    output_path: Optional[Path] = None,
    format: str = "png"
) -> Optional[Path]:
    """
    Create a flowchart diagram.

    Args:
        nodes: List of node dictionaries with 'id' and 'label'.
        edges: List of tuples (from_id, to_id).
        title: Diagram title.
        output_path: Path to save diagram.
        format: Output format (png, svg, pdf).

    Returns:
        Path to generated diagram or None.
    """
    if not GRAPHVIZ_AVAILABLE:
        return None

    dot = graphviz.Digraph(comment=title)
    dot.attr(rankdir='TB')

    # Add nodes
    for node in nodes:
        dot.node(node['id'], node['label'], shape='box', style='rounded')

    # Add edges
    for from_id, to_id in edges:
        dot.edge(from_id, to_id)

    # Render
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        dot.render(str(output_path.with_suffix('')), format=format, cleanup=True)
        return output_path.with_suffix(f'.{format}')

    return None


def create_concept_map(
    concepts: List[str],
    relationships: List[tuple],
    title: str = "Concept Map",
    output_path: Optional[Path] = None,
    format: str = "png"
) -> Optional[Path]:
    """
    Create a concept map diagram.

    Args:
        concepts: List of concept names.
        relationships: List of tuples (concept1, relation, concept2).
        title: Diagram title.
        output_path: Path to save diagram.
        format: Output format.

    Returns:
        Path to generated diagram or None.
    """
    if not GRAPHVIZ_AVAILABLE:
        return None

    dot = graphviz.Graph(comment=title)
    dot.attr('node', shape='ellipse')

    # Add concepts
    for concept in concepts:
        dot.node(concept.replace(' ', '_'), concept)

    # Add relationships
    for concept1, relation, concept2 in relationships:
        dot.edge(
            concept1.replace(' ', '_'),
            concept2.replace(' ', '_'),
            label=relation
        )

    # Render
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        dot.render(str(output_path.with_suffix('')), format=format, cleanup=True)
        return output_path.with_suffix(f'.{format}')

    return None


def create_hierarchy_diagram(
    hierarchy: Dict[str, List[str]],
    title: str = "Hierarchy",
    output_path: Optional[Path] = None,
    format: str = "png"
) -> Optional[Path]:
    """
    Create a hierarchical diagram.

    Args:
        hierarchy: Dictionary mapping parent to list of children.
        title: Diagram title.
        output_path: Path to save diagram.
        format: Output format.

    Returns:
        Path to generated diagram or None.
    """
    if not GRAPHVIZ_AVAILABLE:
        return None

    dot = graphviz.Digraph(comment=title)
    dot.attr(rankdir='TB')
    dot.attr('node', shape='box', style='filled', fillcolor='lightblue')

    # Add all nodes and edges
    for parent, children in hierarchy.items():
        parent_id = parent.replace(' ', '_')
        dot.node(parent_id, parent)

        for child in children:
            child_id = child.replace(' ', '_')
            dot.node(child_id, child)
            dot.edge(parent_id, child_id)

    # Render
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        dot.render(str(output_path.with_suffix('')), format=format, cleanup=True)
        return output_path.with_suffix(f'.{format}')

    return None


def generate_mermaid_diagram(
    mermaid_code: str,
    output_path: Path,
    logger: logging.Logger = None
) -> bool:
    """
    Generate diagram from Mermaid code using mermaid-cli.

    Args:
        mermaid_code: Mermaid diagram code.
        output_path: Output path for diagram.
        logger: Logger instance.

    Returns:
        True if successful, False otherwise.
    """
    # Check if mermaid-cli is available
    try:
        subprocess.run(["mmdc", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        if logger:
            logger.warning("mermaid-cli not available, skipping diagram generation")
        return False

    # Write Mermaid code to temp file
    temp_file = output_path.with_suffix('.mmd')
    with open(temp_file, 'w') as f:
        f.write(mermaid_code)

    # Generate diagram
    try:
        subprocess.run(
            ["mmdc", "-i", str(temp_file), "-o", str(output_path)],
            capture_output=True,
            check=True
        )
        temp_file.unlink()  # Clean up temp file
        return True
    except subprocess.CalledProcessError as e:
        if logger:
            logger.error(f"Failed to generate Mermaid diagram: {e}")
        return False


def detect_diagram_opportunity(text: str) -> Optional[str]:
    """
    Detect if text describes a process that could be diagrammed.

    Args:
        text: Input text.

    Returns:
        Diagram type suggestion or None.
    """
    text_lower = text.lower()

    # Check for process indicators
    process_keywords = ['step', 'process', 'algorithm', 'procedure', 'workflow']
    if any(keyword in text_lower for keyword in process_keywords):
        return 'flowchart'

    # Check for relationship indicators
    relationship_keywords = ['relationship', 'connection', 'related to', 'depends on']
    if any(keyword in text_lower for keyword in relationship_keywords):
        return 'concept_map'

    # Check for hierarchy indicators
    hierarchy_keywords = ['hierarchy', 'parent', 'child', 'inherit', 'derived from']
    if any(keyword in text_lower for keyword in hierarchy_keywords):
        return 'hierarchy'

    return None
