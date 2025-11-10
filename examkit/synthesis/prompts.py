"""
Jinja2 prompt templates for LLM generation.
"""

from jinja2 import Template

# Definition prompt template
DEFINITION_TEMPLATE = """
Given the following context from lecture materials, provide a clear and concise definition of "{{ topic_name }}".

Context:
{% for chunk in context_chunks %}
- {{ chunk.text }} [{{ chunk.source }}]
{% endfor %}

Provide a definition that:
1. Is accurate and grounded in the provided context
2. Uses precise technical terminology
3. Is suitable for exam preparation
4. Cites sources using [{{ chunk.source }}] format

Definition:
"""

# Derivation prompt template
DERIVATION_TEMPLATE = """
Given the following context, provide a step-by-step derivation or explanation of "{{ topic_name }}".

Context:
{% for chunk in context_chunks %}
- {{ chunk.text }} [{{ chunk.source }}]
{% endfor %}

Provide a derivation that:
1. Shows each step clearly
2. Explains the logic behind each transformation
3. Highlights key assumptions
4. Cites sources for each major step

Derivation:
"""

# Common mistakes prompt template
MISTAKES_TEMPLATE = """
Based on the following exam and lecture context for "{{ topic_name }}", identify common mistakes students make.

Context:
{% for chunk in context_chunks %}
- {{ chunk.text }} [{{ chunk.source }}]
{% endfor %}

List 3-5 common mistakes, each with:
1. Description of the mistake
2. Why it occurs
3. How to avoid it
4. Source citations

Common Mistakes:
"""

# Compare and contrast template
COMPARE_TEMPLATE = """
Compare and contrast "{{ topic_a }}" and "{{ topic_b }}" based on the following context.

Context for {{ topic_a }}:
{% for chunk in context_a %}
- {{ chunk.text }} [{{ chunk.source }}]
{% endfor %}

Context for {{ topic_b }}:
{% for chunk in context_b %}
- {{ chunk.text }} [{{ chunk.source }}]
{% endfor %}

Provide a comparison that:
1. Highlights key similarities
2. Identifies important differences
3. Explains when to use each
4. Cites sources appropriately

Comparison:
"""

# Fast revision prompt template
FAST_REVISION_TEMPLATE = """
Create a quick revision summary for "{{ topic_name }}" suitable for last-minute exam preparation.

Context:
{% for chunk in context_chunks %}
- {{ chunk.text }} [{{ chunk.source }}]
{% endfor %}

Create a summary with:
1. Key formula or definition (if applicable)
2. 3-5 bullet points of essential facts
3. One worked example or application
4. Common pitfall to avoid

Revision Summary:
"""

# Worked example template
EXAMPLE_TEMPLATE = """
Based on the following context, create a worked example demonstrating "{{ topic_name }}".

Context:
{% for chunk in context_chunks %}
- {{ chunk.text }} [{{ chunk.source }}]
{% endfor %}

Provide an example with:
1. Clear problem statement
2. Step-by-step solution
3. Final answer
4. Explanation of key concepts used
5. Source citations

Worked Example:
"""


def render_definition_prompt(topic_name: str, context_chunks: list) -> str:
    """
    Render a definition prompt for the given topic using the module's Jinja2 template.
    
    Parameters:
        topic_name (str): The topic name to insert into the prompt.
        context_chunks (list): Sequence of context chunks used to populate the prompt; each chunk is expected to include source metadata and the chunk content.
    
    Returns:
        str: The rendered prompt text.
    """
    template = Template(DEFINITION_TEMPLATE)
    return template.render(topic_name=topic_name, context_chunks=context_chunks)


def render_derivation_prompt(topic_name: str, context_chunks: list) -> str:
    """
    Render a filled derivation prompt for a given topic using provided context chunks.
    
    Parameters:
        topic_name (str): Name of the topic to derive.
        context_chunks (list): Iterable of context chunk objects or dicts; each chunk should include source and content used to cite and support the derivation.
    
    Returns:
        str: The rendered prompt text with a Derivation section and inline source citations.
    """
    template = Template(DERIVATION_TEMPLATE)
    return template.render(topic_name=topic_name, context_chunks=context_chunks)


def render_mistakes_prompt(topic_name: str, context_chunks: list) -> str:
    """
    Builds a prompt that asks for common mistakes related to a topic using the provided context chunks.
    
    Parameters:
        context_chunks (list): Sequence of context items (e.g., mappings with source and content) to be embedded into the prompt as cited sources.
    
    Returns:
        str: The rendered prompt text.
    """
    template = Template(MISTAKES_TEMPLATE)
    return template.render(topic_name=topic_name, context_chunks=context_chunks)


def render_compare_prompt(topic_a: str, topic_b: str, context_a: list, context_b: list) -> str:
    """
    Builds a compare-and-contrast prompt for two topics using their context chunks.
    
    Parameters:
        topic_a (str): Name of the first topic.
        topic_b (str): Name of the second topic.
        context_a (list): Context chunks (source/text entries) related to `topic_a`.
        context_b (list): Context chunks (source/text entries) related to `topic_b`.
    
    Returns:
        str: The rendered prompt text that instructs an LLM to compare similarities, differences,
        appropriate usages, and provide source-cited conclusions for the two topics.
    """
    template = Template(COMPARE_TEMPLATE)
    return template.render(topic_a=topic_a, topic_b=topic_b, context_a=context_a, context_b=context_b)


def render_revision_prompt(topic_name: str, context_chunks: list) -> str:
    """
    Builds a quick revision prompt for a topic using the provided context chunks.
    
    Parameters:
    	topic_name (str): The topic title to include in the prompt.
    	context_chunks (list): Sequence of context chunk objects (e.g., mappings with `source` and content) whose sources and content will be listed and cited in the prompt.
    
    Returns:
    	rendered_prompt (str): The rendered revision prompt text containing a concise revision summary, key facts, a worked example, and source citations.
    """
    template = Template(FAST_REVISION_TEMPLATE)
    return template.render(topic_name=topic_name, context_chunks=context_chunks)


def render_example_prompt(topic_name: str, context_chunks: list) -> str:
    """
    Builds a worked-example prompt for a topic using the provided context chunks.
    
    Parameters:
    	topic_name (str): The topic title to include in the prompt.
    	context_chunks (list): Iterable of context items (each supplying content and source) to be incorporated and cited in the prompt.
    
    Returns:
    	rendered_prompt (str): The prompt text produced by rendering the worked-example template with the given topic and context chunks.
    """
    template = Template(EXAMPLE_TEMPLATE)
    return template.render(topic_name=topic_name, context_chunks=context_chunks)