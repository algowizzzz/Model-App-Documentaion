"""
Test script for verifying the loader and parser functionality.
"""

from src.data.loader import load_codebase, load_template
from src.data.schema import ParsedFile, CodeChunk

def test_python_file_loading():
    """Test loading and parsing of our test Python file."""
    
    # Load the test codebase
    result = load_codebase("test_codebase", parse_chunks=True)
    
    # Basic file loading checks
    assert "test_sample.py" in result, "Test file not found in results"
    assert isinstance(result["test_sample.py"], ParsedFile), "Result should be a ParsedFile object"
    
    parsed_file = result["test_sample.py"]
    print("\n=== File Level Information ===")
    print(f"File path: {parsed_file.file_path}")
    print(f"Language: {parsed_file.language}")
    print(f"Number of chunks: {len(parsed_file.chunks)}")
    
    # Check top-level chunks
    print("\n=== Top Level Chunks ===")
    for chunk in parsed_file.chunks:
        print(f"\nChunk: {chunk.name} (Type: {chunk.chunk_type})")
        print(f"Line range: {chunk.line_range}")
        print(f"Docstring: {chunk.docstring}")
        
        if chunk.metadata and "parameters" in chunk.metadata:
            print(f"Parameters: {chunk.metadata['parameters']}")
        if chunk.metadata and "return_type" in chunk.metadata:
            print(f"Return Type: {chunk.metadata['return_type']}")
        
        # If it's a class, check its methods
        if chunk.chunk_type == "class" and chunk.metadata and "methods" in chunk.metadata:
            print("\n  Class Methods:")
            for method in chunk.metadata["methods"]:
                print(f"  - {method.name}")
                print(f"    Type: {method.chunk_type}")
                print(f"    Line range: {method.line_range}")
                print(f"    Docstring: {method.docstring}")
                if method.metadata and "parameters" in method.metadata:
                    print(f"    Parameters: {method.metadata['parameters']}")
                if method.metadata and "return_type" in method.metadata:
                    print(f"    Return Type: {method.metadata['return_type']}")

def test_non_python_files():
    """Test loading and handling of non-Python files."""
    print("\n=== Testing Non-Python File Handling ===")
    
    result = load_codebase("test_codebase", parse_chunks=True)
    
    # Test JavaScript file (parseable but not Python)
    print("\n--- JavaScript File ---")
    assert "app.js" in result, "JavaScript file not found"
    js_file = result["app.js"]
    assert isinstance(js_file, ParsedFile), "JavaScript file should be parsed into ParsedFile"
    print(f"Language: {js_file.language}")
    print(f"Number of chunks: {len(js_file.chunks)}")  # Should be 0 as we don't parse JS yet
    print(f"Has content: {'full_content' in js_file.__dict__ and bool(js_file.full_content)}")
    
    # Test Markdown file (non-parseable)
    print("\n--- Markdown File ---")
    assert "readme.md" in result, "Markdown file not found"
    md_content = result["readme.md"]
    assert isinstance(md_content, str), "Markdown should be stored as raw string"
    print(f"Content type: {type(md_content)}")
    print(f"Content length: {len(md_content)} characters")
    
    # Test JSON file (non-parseable)
    print("\n--- JSON File ---")
    assert "config.json" in result, "JSON file not found"
    json_content = result["config.json"]
    assert isinstance(json_content, str), "JSON should be stored as raw string"
    print(f"Content type: {type(json_content)}")
    print(f"Content length: {len(json_content)} characters")

def test_error_handling():
    """Test error handling for various edge cases."""
    print("\n=== Testing Error Handling ===")
    
    result = load_codebase("test_codebase", parse_chunks=True)
    
    # Test invalid Python syntax
    print("\n--- Invalid Python Syntax ---")
    assert "invalid_syntax.py" in result, "Invalid syntax file not found"
    invalid_file = result["invalid_syntax.py"]
    # Should still be loaded but as raw string due to parsing failure
    assert isinstance(invalid_file, str), "Invalid Python file should be stored as raw string"
    print(f"Invalid Python file handled as: {type(invalid_file)}")
    
    # Test binary file exclusion
    print("\n--- Binary File Handling ---")
    assert "binary_file.bin" not in result, "Binary file should be excluded"
    print("Binary file successfully excluded")
    
    # Test hidden file exclusion
    print("\n--- Hidden File Handling ---")
    assert ".hidden_file.py" not in result, "Hidden file should be excluded"
    print("Hidden file successfully excluded")
    
    # Test non-existent directory
    print("\n--- Non-existent Directory ---")
    empty_result = load_codebase("non_existent_dir", parse_chunks=True)
    assert isinstance(empty_result, dict) and len(empty_result) == 0, "Non-existent directory should return empty dict"
    print("Non-existent directory handled correctly")

def test_template_loading():
    """Test loading of documentation templates."""
    print("\n=== Testing Template Loading ===")
    
    # Test valid template
    print("\n--- Valid Template ---")
    valid_template = load_template("test_codebase/templates/valid_template.json")
    assert valid_template, "Valid template should be loaded"
    assert "template_version" in valid_template, "Template should have version"
    assert "sections" in valid_template, "Template should have sections"
    print("Valid template loaded successfully")
    print(f"Template version: {valid_template.get('template_version')}")
    print(f"Number of sections: {len(valid_template.get('sections', {}))}")
    
    # Test invalid template
    print("\n--- Invalid Template ---")
    invalid_template = load_template("test_codebase/templates/invalid_template.json")
    assert not invalid_template, "Invalid template should return empty dict"
    print("Invalid template handled correctly")
    
    # Test non-existent template
    print("\n--- Non-existent Template ---")
    missing_template = load_template("test_codebase/templates/missing.json")
    assert not missing_template, "Missing template should return empty dict"
    print("Non-existent template handled correctly")

def test_language_detection():
    """Test language detection for various file types."""
    print("\n=== Testing Language Detection ===")
    
    result = load_codebase("test_codebase", parse_chunks=True)
    
    # Test Python detection
    print("\n--- Python Files ---")
    assert isinstance(result["test_sample.py"], ParsedFile), "Python file not properly detected"
    assert result["test_sample.py"].language == "python", "Python language not properly detected"
    print("Python detection successful")
    
    # Test JavaScript detection
    print("\n--- JavaScript Files ---")
    assert isinstance(result["app.js"], ParsedFile), "JavaScript file not properly detected"
    assert result["app.js"].language == "javascript", "JavaScript language not properly detected"
    print("JavaScript detection successful")
    
    # Test CSS detection
    print("\n--- CSS Files ---")
    assert "styles.css" in result, "CSS file not found"
    css_file = result["styles.css"]
    assert isinstance(css_file, str), "CSS should be stored as raw string"
    print("CSS handling successful")
    
    # Test XML detection
    print("\n--- XML Files ---")
    assert "data.xml" in result, "XML file not found"
    xml_file = result["data.xml"]
    assert isinstance(xml_file, str), "XML should be stored as raw string"
    print("XML handling successful")
    
    # Test SQL detection
    print("\n--- SQL Files ---")
    assert "query.sql" in result, "SQL file not found"
    sql_file = result["query.sql"]
    assert isinstance(sql_file, str), "SQL should be stored as raw string"
    print("SQL handling successful")

if __name__ == "__main__":
    print("Testing Python file parsing...")
    test_python_file_loading()
    print("\nTesting non-Python file handling...")
    test_non_python_files()
    print("\nTesting error handling...")
    test_error_handling()
    print("\nTesting template loading...")
    test_template_loading()
    print("\nTesting language detection...")
    test_language_detection() 