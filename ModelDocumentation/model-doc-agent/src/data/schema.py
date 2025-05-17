from typing import Dict, List, Any, Optional

class CodeChunk:
    """Represents a logical chunk of code (e.g., function, class, method)."""
    
    def __init__(self, 
                 name: str, 
                 type: str,  # e.g., 'function', 'class', 'method'
                 source_code: str, 
                 start_line: int, 
                 end_line: int,
                 parent_name: Optional[str] = None, # Name of parent class if this is a method
                 docstring: Optional[str] = None,
                 parameters: Optional[Dict[str, Any]] = None, # For functions/methods
                 return_type: Optional[str] = None # For functions/methods
                 ):
        self.name = name
        self.type = type
        self.source_code = source_code
        self.start_line = start_line
        self.end_line = end_line
        self.parent_name = parent_name
        self.docstring = docstring
        self.parameters = parameters if parameters else {}
        self.return_type = return_type
        self.children: List[CodeChunk] = [] # For methods within classes, or nested functions/classes
        
    def add_child(self, child: 'CodeChunk'):
        """Add a child chunk (e.g., a method to a class, or a nested function)."""
        self.children.append(child)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert CodeChunk instance to a dictionary representation."""
        data = {
            'name': self.name,
            'type': self.type,
            'source_code': self.source_code,
            'start_line': self.start_line,
            'end_line': self.end_line,
            'parent_name': self.parent_name,
            'docstring': self.docstring,
            'parameters': self.parameters,
            'return_type': self.return_type,
            'children_count': len(self.children)
        }
        if self.children:
            data['children'] = [child.to_dict() for child in self.children]
        return data

    def __repr__(self) -> str:
        return f"CodeChunk(name='{self.name}', type='{self.type}', lines={self.start_line}-{self.end_line})"

class ParsedFile:
    """Represents a parsed code file with its content and extracted chunks."""
    def __init__(self, 
                 file_path: str,
                 full_content: str,
                 chunks: List[CodeChunk]):
        self.file_path = file_path
        self.full_content = full_content
        self.chunks = chunks

    def to_dict(self) -> Dict[str, Any]:
        return {
            'file_path': self.file_path,
            'line_count': len(self.full_content.splitlines()),
            'chunk_count': len(self.chunks),
            'chunks': [chunk.to_dict() for chunk in self.chunks]
            # Add full_content if needed, but can be large
            # 'full_content': self.full_content 
        }

    def __repr__(self) -> str:
        return f"ParsedFile(file_path='{self.file_path}', chunks={len(self.chunks)})" 