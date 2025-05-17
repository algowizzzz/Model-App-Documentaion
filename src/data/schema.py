"""
Schema definitions for data structures used in the Model Documentation Agent.
"""

from typing import List, Dict, Optional, Union, Any
from dataclasses import dataclass

@dataclass
class CodeChunk:
    """
    Represents a chunk of code (e.g., function, class, method).
    """
    name: str
    content: str
    docstring: Optional[str] = None
    chunk_type: str = "unknown"  # e.g., function, class, method
    line_range: tuple[int, int] = (0, 0)  # start and end line
    parent: Optional[str] = None  # parent chunk name if applicable
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
            
    def __str__(self) -> str:
        return f"{self.chunk_type}: {self.name} ({self.line_range[0]}-{self.line_range[1]})"
    
@dataclass
class ParsedFile:
    """
    Represents a parsed code file with extracted chunks and metadata.
    """
    file_path: str  # Path relative to codebase root
    full_content: str  # Full file content
    language: str  # Programming language (e.g., python, javascript)
    chunks: List[CodeChunk]  # Extracted code chunks
    imports: List[str] = None  # Imported modules/packages
    file_docstring: Optional[str] = None  # File-level docstring
    metadata: Dict[str, Any] = None  # Additional metadata
    
    def __post_init__(self):
        if self.imports is None:
            self.imports = []
        if self.metadata is None:
            self.metadata = {}
            
    def __str__(self) -> str:
        return f"ParsedFile: {self.file_path} ({self.language}, {len(self.chunks)} chunks)"
    
    def get_chunk_by_name(self, name: str) -> Optional[CodeChunk]:
        """
        Get a code chunk by its name.
        
        Args:
            name: Name of the chunk
            
        Returns:
            CodeChunk or None if not found
        """
        for chunk in self.chunks:
            if chunk.name == name:
                return chunk
        return None
    
    def get_chunks_by_type(self, chunk_type: str) -> List[CodeChunk]:
        """
        Get all code chunks of a specific type.
        
        Args:
            chunk_type: Type of chunks to get
            
        Returns:
            List of CodeChunks
        """
        return [chunk for chunk in self.chunks if chunk.chunk_type == chunk_type] 