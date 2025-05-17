import ast
from typing import List, Optional, Dict, Any
from .schema import CodeChunk, ParsedFile

class PythonCodeParser:
    """Enhanced Python code parser that extracts logical chunks (functions and classes)."""
    
    def parse_file_content(self, file_content: str, file_path: str = "<string>") -> ParsedFile:
        """
        Parse Python file content into a structured representation with logical chunks.

        Parameters:
        -----------
        file_content : str
            The Python code as a string.
        file_path : str, optional
            The original path of the file, for context.

        Returns:
        --------
        ParsedFile: An object containing the full content and a list of CodeChunk objects.
        
        Raises:
        -------
        SyntaxError: If the Python code is invalid.
        """
        tree = ast.parse(file_content)
        source_lines = file_content.splitlines()
        
        chunks: List[CodeChunk] = []
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                chunk = self._extract_function_or_method(node, source_lines)
                chunks.append(chunk)
            elif isinstance(node, ast.ClassDef):
                chunk = self._extract_class(node, source_lines)
                chunks.append(chunk)
                
        return ParsedFile(
            file_path=file_path,
            full_content=file_content,
            language="python",
            chunks=chunks
        )

    def _get_node_source(self, node: ast.AST, source_lines: List[str]) -> str:
        """Extracts the source code for a given AST node."""
        start_line = node.lineno - 1
        end_line = node.end_lineno if hasattr(node, 'end_lineno') and node.end_lineno is not None else start_line + 1
        end_line = min(end_line, len(source_lines))
        return '\n'.join(source_lines[start_line:end_line])

    def _extract_function_or_method(self, 
                                 node: ast.FunctionDef | ast.AsyncFunctionDef, 
                                 source_lines: List[str], 
                                 parent_class_name: Optional[str] = None) -> CodeChunk:
        """Extracts a function or method definition."""
        name = node.name
        start_line = node.lineno
        end_line = node.end_lineno if hasattr(node, 'end_lineno') and node.end_lineno is not None else start_line
        source_code = self._get_node_source(node, source_lines)
        docstring = ast.get_docstring(node)
        
        # Determine chunk type
        chunk_type = 'method' if parent_class_name else ('async_function' if isinstance(node, ast.AsyncFunctionDef) else 'function')
        
        # Extract parameters
        parameters = {}
        for arg in node.args.args:
            param_name = arg.arg
            param_type = ast.unparse(arg.annotation) if hasattr(arg, 'annotation') and arg.annotation else None
            parameters[param_name] = {"type": param_type, "default": None}
        
        if node.args.vararg:
            parameters[node.args.vararg.arg] = {"type": "*args", "default": None}
        if node.args.kwarg:
            parameters[node.args.kwarg.arg] = {"type": "**kwargs", "default": None}

        return_type = ast.unparse(node.returns) if hasattr(node, 'returns') and node.returns else None
        
        metadata = {
            "parameters": parameters,
            "return_type": return_type
        }
        
        chunk = CodeChunk(
            name=name,
            content=source_code,
            docstring=docstring,
            chunk_type=chunk_type,
            line_range=(start_line, end_line),
            parent=parent_class_name,
            metadata=metadata
        )
        
        return chunk

    def _extract_class(self, node: ast.ClassDef, source_lines: List[str], parent_name: Optional[str] = None) -> CodeChunk:
        """Extracts a class definition, including its methods and nested classes."""
        name = node.name
        start_line = node.lineno
        end_line = node.end_lineno if hasattr(node, 'end_lineno') and node.end_lineno is not None else start_line
        source_code = self._get_node_source(node, source_lines)
        docstring = ast.get_docstring(node)

        class_chunk = CodeChunk(
            name=name,
            content=source_code,
            docstring=docstring,
            chunk_type='class',
            line_range=(start_line, end_line),
            parent=parent_name
        )
        
        # Store methods in metadata
        methods = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_chunk = self._extract_function_or_method(item, source_lines, parent_class_name=name)
                methods.append(method_chunk)
            elif isinstance(item, ast.ClassDef):
                nested_class_chunk = self._extract_class(item, source_lines, parent_name=name)
                methods.append(nested_class_chunk)
        
        if methods:
            if class_chunk.metadata is None:
                class_chunk.metadata = {}
            class_chunk.metadata["methods"] = methods
        
        return class_chunk

# Example Usage (for testing)
if __name__ == '__main__':
    sample_code = """
import os

class MyClass:
    \"\"\"This is MyClass docstring.\"\"\"
    class_var = 10

    def __init__(self, value: int):
        \"\"\"Constructor docstring.\"\"\"
        self.value = value

    async def my_method(self, param1: str) -> str:
        \"\"\"This is my_method docstring.\"\"\"
        def nested_func(x):
            return x * 2
        return f\"Hello {param1}, {self.value}, {nested_func(3)}\"

def my_function(a: int, b: str = \"test\") -> dict:
    \"\"\"This is my_function docstring.\"\"\"
    return {"a": a, "b": b}
    """

    parser = PythonCodeParser()
    try:
        parsed_file_obj = parser.parse_file_content(sample_code, "sample.py")
        print(f"Parsed file: {parsed_file_obj.file_path}")
        print(f"Total lines: {len(parsed_file_obj.full_content.splitlines())}")
        print(f"Found {len(parsed_file_obj.chunks)} top-level chunks:")
        for i, chunk_obj in enumerate(parsed_file_obj.chunks):
            print(f"  Chunk {i+1}: {chunk_obj.name} (Type: {chunk_obj.chunk_type}, Lines: {chunk_obj.line_range[0]}-{chunk_obj.line_range[1]})")
            print(f"    Docstring: {chunk_obj.docstring}")
            print(f"    Parameters: {chunk_obj.metadata['parameters']}")
            print(f"    Return Type: {chunk_obj.metadata['return_type']}")
            if chunk_obj.children:
                print(f"    Found {len(chunk_obj.children)} nested chunks:")
                for j, child in enumerate(chunk_obj.children):
                    print(f"      Nested {j+1}: {child.name} (Type: {child.chunk_type}, Lines: {child.line_range[0]}-{child.line_range[1]})")
                    print(f"        Docstring: {child.docstring}")

        # Test to_dict method
        # import json
        # print("\nParsed File as Dict:")
        # print(json.dumps(parsed_file_obj.to_dict(), indent=2))

    except SyntaxError as e:
        print(f"Syntax Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc() 