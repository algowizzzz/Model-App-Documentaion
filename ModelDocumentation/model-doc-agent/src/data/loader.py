import json
import os
from typing import List, Dict, Union
from pathlib import Path

from ..utils.config import Config
from ..debug.logger import ModelDocDebugger
from .chunk_parser import PythonCodeParser
from .schema import ParsedFile, CodeChunk

# Initialize debugger (or get a shared instance)
# For simplicity, instantiating one here. In a larger app, this might be passed around.
debugger = ModelDocDebugger(logger_name="DataLoader", debug_level="INFO")
config = Config() # Using a default config instance

@debugger.time_function
def load_code_from_directory(code_dir: str, parse_chunks: bool = True) -> Dict[str, Union[str, ParsedFile]]:
    """
    Read all supported files in the code_dir into a dict mapping filename to content or ParsedFile object.

    Parameters:
    -----------
    code_dir : str
        The directory to scan for code files.
    parse_chunks : bool, optional
        If True, parses Python files into CodeChunk objects. 
        If False, returns raw file content for all files. Defaults to True.

    Returns:
    --------
    Dict[str, Union[str, ParsedFile]]:
        A dictionary where keys are relative file paths and values are either 
        ParsedFile objects (for successfully parsed Python files if parse_chunks is True) 
        or raw file content strings (for other files or if parse_chunks is False).
    """
    processed_files: Dict[str, Union[str, ParsedFile]] = {}
    code_dir_path = Path(code_dir)
    
    if not code_dir_path.is_dir():
        debugger.logger.error(f"Code directory not found or is not a directory: {code_dir}")
        raise FileNotFoundError(f"Code directory not found: {code_dir}")

    supported_extensions = config.get("codebase.extensions", [".py", ".sql", ".json", ".yml", ".yaml"])
    excluded_dirs = set(config.get("codebase.exclude_dirs", ["__pycache__", ".git", "venv", ".DS_Store"]))
    python_parser_enabled = config.get("parser.python.enabled", True)
    
    python_parser = PythonCodeParser() if python_parser_enabled and parse_chunks else None

    debugger.logger.info(f"Starting codebase load from directory: {code_dir_path}")
    debugger.logger.debug(f"Supported extensions: {supported_extensions}")
    debugger.logger.debug(f"Excluded directories: {excluded_dirs}")

    for item_path in code_dir_path.rglob("*"): # rglob for recursive walk
        if any(excluded_part in item_path.parts for excluded_part in excluded_dirs):
            if item_path.is_dir():
                 debugger.logger.debug(f"Skipping excluded directory: {item_path}")
            continue # Skip if part of an excluded directory path

        if item_path.is_file() and item_path.suffix in supported_extensions:
            relative_path_str = str(item_path.relative_to(code_dir_path))
            debugger.logger.debug(f"Processing file: {relative_path_str}")
            try:
                with open(item_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if item_path.suffix == '.py' and python_parser:
                    try:
                        parsed_file_obj = python_parser.parse_file_content(content, str(item_path))
                        processed_files[relative_path_str] = parsed_file_obj
                        debugger.logger.debug(f"Successfully parsed Python file into chunks: {relative_path_str}")
                    except SyntaxError as se:
                        debugger.logger.warning(f"Syntax error parsing Python file {relative_path_str}, storing raw content. Error: {se}")
                        processed_files[relative_path_str] = content # Fallback to raw content
                    except Exception as e_parse:
                        debugger.log_exception("PythonCodeParser.parse_file_content", e_parse, {"file": relative_path_str})
                        processed_files[relative_path_str] = content # Fallback to raw content
                else:
                    processed_files[relative_path_str] = content
                    if item_path.suffix == '.py' and not python_parser:
                        debugger.logger.debug(f"Stored raw content for Python file (chunk parsing disabled): {relative_path_str}")
                    else:
                        debugger.logger.debug(f"Stored raw content for non-Python file: {relative_path_str}")

            except FileNotFoundError:
                debugger.logger.error(f"File not found during processing (should not happen with rglob): {item_path}")
            except UnicodeDecodeError as ude:
                debugger.logger.warning(f"Unicode decode error for file {relative_path_str}. Storing as raw bytes or skipping. Error: {ude}")
                # Optionally, try to read as bytes and store, or skip
            except Exception as e_read:
                debugger.log_exception("load_code_from_directory.read_file", e_read, {"file": relative_path_str})
        elif item_path.is_dir():
             debugger.logger.debug(f"Scanning directory: {item_path}")

    if not processed_files:
        debugger.logger.warning(f"No processable code files found in {code_dir_path} with current settings.")
        # Not raising an error, as an empty directory might be valid in some contexts.

    debugger.logger.info(f"Finished codebase load. Processed {len(processed_files)} files.")
    return processed_files

@debugger.time_function
def load_documentation_template(template_path: str) -> Dict:
    """
    Load documentation template JSON defining sections and prompts per codebase type.

    Parameters:
    -----------
    template_path : str
        Path to the JSON documentation template file.

    Returns:
    --------
    Dict:
        The loaded template as a dictionary.

    Raises:
    -------
    FileNotFoundError: If the template file is not found.
    json.JSONDecodeError: If the template file is not valid JSON.
    """
    template_file = Path(template_path)
    debugger.logger.info(f"Loading documentation template from: {template_file}")
    if not template_file.is_file():
        debugger.logger.error(f"Template file not found: {template_path}")
        raise FileNotFoundError(f"Template file not found: {template_path}")
    
    try:
        with open(template_file, 'r', encoding='utf-8') as f:
            template_data = json.load(f)
        debugger.logger.debug(f"Successfully loaded template: {template_path}")
        return template_data
    except json.JSONDecodeError as e_json:
        debugger.logger.error(f"Invalid JSON in template file {template_path}: {e_json}")
        raise # Re-raise to signal failure to the caller
    except Exception as e_read:
        debugger.log_exception("load_documentation_template.read_file", e_read, {"template_path": template_path})
        raise

# Renaming old functions to reflect their new behavior or for clarity
load_codebase = load_code_from_directory
load_template = load_documentation_template


# Example Usage (for testing, if this file is run directly)
if __name__ == '__main__':
    # Create a dummy config and debugger for standalone testing
    # In real use, these would be part of the application context
    print("Running loader.py standalone test...")
    test_config_path = "./dummy_config.json"
    # with open(test_config_path, "w") as f:
    #     json.dump({"codebase": {"extensions": [".py"]}}, f)
    
    # config = Config(test_config_path)
    # debugger = ModelDocDebugger(debug_level="DEBUG")

    # Create dummy files and directories for testing
    test_code_dir = Path("__test_code_dir__")
    test_code_dir.mkdir(exist_ok=True)
    (test_code_dir / "file1.py").write_text("def foo():\n  pass\n\nclass Bar:\n  def baz(self):\n    return 1")
    (test_code_dir / "file2.txt").write_text("Some text data")
    (test_code_dir / "excluded_dir").mkdir(exist_ok=True)
    (test_code_dir / "excluded_dir" / "file3.py").write_text("print('excluded')")
    
    # Create a dummy template
    dummy_template_path = Path("__dummy_template.json__")
    with open(dummy_template_path, 'w') as f:
        json.dump({"name": "Test Template", "sections": []}, f)

    print(f"\n--- Testing load_codebase (with chunk parsing) ---")
    try:
        loaded_code = load_codebase(str(test_code_dir), parse_chunks=True)
        for path, data in loaded_code.items():
            print(f"File: {path}")
            if isinstance(data, ParsedFile):
                print(f"  Type: ParsedFile, Chunks: {len(data.chunks)}")
                for chunk in data.chunks:
                    print(f"    Chunk: {chunk.name} ({chunk.type}) Doc: {chunk.docstring}")
            else:
                print(f"  Type: Raw Content (length: {len(data)})")
        # Expected: file1.py (ParsedFile), file2.txt (str)
    except Exception as e:
        print(f"Error during load_codebase test: {e}")
        import traceback
        traceback.print_exc()

    print(f"\n--- Testing load_codebase (no chunk parsing) ---")
    try:
        loaded_code_raw = load_codebase(str(test_code_dir), parse_chunks=False)
        for path, data in loaded_code_raw.items():
            print(f"File: {path}")
            print(f"  Type: Raw Content (length: {len(data)})")
        # Expected: file1.py (str), file2.txt (str)
    except Exception as e:
        print(f"Error during load_codebase (raw) test: {e}")

    print(f"\n--- Testing load_template ---")
    try:
        template = load_template(str(dummy_template_path))
        print(f"Loaded template: {template.get('name')}")
    except Exception as e:
        print(f"Error during load_template test: {e}")

    # Cleanup dummy files and directories
    import shutil
    (test_code_dir / "file1.py").unlink()
    (test_code_dir / "file2.txt").unlink()
    (test_code_dir / "excluded_dir" / "file3.py").unlink()
    (test_code_dir / "excluded_dir").rmdir()
    test_code_dir.rmdir()
    dummy_template_path.unlink()
    # if os.path.exists(test_config_path):
    #     os.unlink(test_config_path)
    print("\nTest cleanup complete.") 