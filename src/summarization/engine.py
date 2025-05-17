"""
Summarization engine for generating various levels of code summaries.
"""

from typing import Dict, List, Any, Optional
from src.data.schema import ParsedFile, CodeChunk
from src.utils.llm_factory import generate_text

def generate_file_summary(file: ParsedFile) -> str:
    """Generate a high-level summary of a file.
    
    Args:
        file: ParsedFile object containing the file content and chunks
        
    Returns:
        A string containing a concise summary of the file's purpose and contents
    """
    # Prepare context from file information
    context = {
        "file_path": file.file_path,
        "language": file.language,
        "docstring": file.file_docstring,
        "num_chunks": len(file.chunks),
        "chunk_names": [chunk.name for chunk in file.chunks]
    }
    
    # Create prompt for file summary
    prompt = f"""
    Please provide a concise summary of this {file.language} file.
    
    File: {context['file_path']}
    Docstring: {context['docstring']}
    Contains {context['num_chunks']} major components: {', '.join(context['chunk_names'])}
    
    Full content:
    {file.full_content}
    
    Provide a summary that:
    1. Explains the main purpose of the file
    2. Lists key components/classes/functions
    3. Highlights important relationships between components
    4. Notes any significant patterns or design choices
    
    Summary:
    """
    
    # Generate summary using LLM
    return generate_text(prompt).strip()

def generate_chunk_summary(chunk: CodeChunk) -> str:
    """Generate a summary of a specific code chunk.
    
    Args:
        chunk: CodeChunk object representing a function, class, or other code unit
        
    Returns:
        A string containing a concise summary of the chunk's purpose and behavior
    """
    # Prepare context from chunk information
    context = {
        "name": chunk.name,
        "type": chunk.chunk_type,
        "docstring": chunk.docstring,
        "line_range": chunk.line_range,
        "metadata": chunk.metadata
    }
    
    # Create prompt for chunk summary
    prompt = f"""
    Please provide a concise summary of this code chunk.
    
    Name: {context['name']}
    Type: {context['type']}
    Docstring: {context['docstring']}
    Lines: {context['line_range'][0]}-{context['line_range'][1]}
    
    Code content:
    {chunk.content}
    
    Additional metadata:
    {context['metadata']}
    
    Provide a summary that:
    1. Explains the specific purpose of this {context['type']}
    2. Describes key functionality and behavior
    3. Notes important parameters, return values, or side effects
    4. Highlights any complex logic or important implementation details
    
    Summary:
    """
    
    # Generate summary using LLM
    return generate_text(prompt).strip()

def generate_hierarchical_summary(file_summaries: Dict[str, str]) -> str:
    """Generate a hierarchical summary from multiple file summaries.
    
    Args:
        file_summaries: Dictionary mapping file paths to their summaries
        
    Returns:
        A string containing a consolidated hierarchical summary
    """
    # Format the summaries for the prompt
    formatted_summaries = "\n\n".join([
        f"File: {file_path}\nSummary:\n{summary}"
        for file_path, summary in file_summaries.items()
        if not summary.startswith("Error")  # Skip error messages
    ])
    
    # Create prompt for hierarchical summary
    prompt = f"""
    Please analyze these file summaries and create a hierarchical summary of the entire codebase.
    
    File Summaries:
    {formatted_summaries}
    
    Create a hierarchical summary that:
    1. Groups related files and components together
    2. Identifies the main modules and their purposes
    3. Explains the relationships between different parts of the codebase
    4. Highlights the overall architecture and design patterns
    
    The summary should start with a high-level overview, then break down into logical components.
    
    Hierarchical Summary:
    """
    
    # Generate summary using LLM
    return generate_text(prompt).strip() 