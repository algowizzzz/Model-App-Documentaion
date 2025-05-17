"""
Data loading utilities for the Model Documentation Agent.
"""

import os
import json
import glob
from typing import Dict, Any, List, Optional, Union
import logging

from src.data.schema import ParsedFile, CodeChunk
from src.data.chunk_parser import PythonCodeParser

logger = logging.getLogger(__name__)

# Initialize parser once
python_parser = PythonCodeParser()

def load_codebase(base_dir: str, parse_chunks: bool = True) -> Dict[str, Union[ParsedFile, str]]:
    """
    Load and parse all code files from a directory.
    
    Args:
        base_dir: Base directory path
        parse_chunks: Whether to parse code into chunks
        
    Returns:
        Dictionary mapping file paths to ParsedFile objects or raw content
    """
    logger.info(f"Loading codebase from: {base_dir}")
    
    if not os.path.exists(base_dir):
        logger.warning(f"Directory does not exist: {base_dir}")
        return {}
    
    result: Dict[str, Union[ParsedFile, str]] = {}
    
    # Walk through all files in the directory
    for root, _, files in os.walk(base_dir):
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, base_dir)
            
            # Skip hidden files and directories
            if file.startswith('.') or any(part.startswith('.') for part in rel_path.split(os.sep)):
                logger.debug(f"Skipping hidden file: {rel_path}")
                continue
                
            # Skip binary files and common non-code files
            if _is_excluded_file(file):
                logger.debug(f"Skipping excluded file: {rel_path}")
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                if parse_chunks and _is_parseable(file):
                    language = _detect_language(file)
                    if language == 'python':
                        try:
                            # Try to parse Python file
                            parsed_file = python_parser.parse_file_content(content, rel_path)
                            result[rel_path] = parsed_file
                        except SyntaxError as e:
                            # If parsing fails, store as raw string
                            logger.warning(f"Failed to parse Python file {rel_path}: {str(e)}")
                            result[rel_path] = content
                        except Exception as e:
                            logger.error(f"Error parsing Python file {rel_path}: {str(e)}")
                            result[rel_path] = content
                    else:
                        # For other parseable languages (future implementation)
                        parsed_file = ParsedFile(
                            file_path=rel_path,
                            full_content=content,
                            language=language,
                            chunks=[],  # Empty chunks for non-Python files for now
                            imports=[],
                            file_docstring=None
                        )
                        result[rel_path] = parsed_file
                else:
                    # Store raw content for non-parseable files
                    result[rel_path] = content
                    
            except UnicodeDecodeError:
                logger.debug(f"Skipping binary file: {rel_path}")
                continue
            except Exception as e:
                logger.error(f"Error loading file {rel_path}: {str(e)}")
                continue
    
    logger.info(f"Loaded {len(result)} files from {base_dir}")
    return result

def load_template(template_path: str) -> Dict[str, Any]:
    """
    Load a documentation template from a JSON file.
    
    Args:
        template_path: Path to the template JSON file
        
    Returns:
        Template data as a dictionary
    """
    logger.info(f"Loading template from: {template_path}")
    
    if not os.path.exists(template_path):
        logger.warning(f"Template file does not exist: {template_path}")
        return {}
        
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = json.load(f)
        logger.info(f"Successfully loaded template: {template_path}")
        return template
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing template JSON {template_path}: {str(e)}")
        return {}
    except Exception as e:
        logger.error(f"Error loading template {template_path}: {str(e)}")
        return {}

def _is_excluded_file(filename: str) -> bool:
    """Check if a file should be excluded based on its extension."""
    excluded_extensions = {
        # Binary files
        '.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe', '.obj', '.o',
        '.a', '.lib', '.bin', '.out', '.app',
        
        # Compressed files
        '.zip', '.tar', '.gz', '.7z', '.rar', '.bz2',
        
        # Media files
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg',
        '.mp3', '.mp4', '.avi', '.mov', '.wav', '.flac',
        
        # Document files
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        
        # Database files
        '.db', '.sqlite', '.sqlite3', '.mdb',
        
        # Cache and system files
        '.cache', '.tmp', '.temp', '.swp', '.DS_Store',
        
        # Other binary formats
        '.jar', '.war', '.class', '.pkl', '.h5', '.model'
    }
    
    _, ext = os.path.splitext(filename.lower())
    return ext in excluded_extensions

def _is_parseable(filename: str) -> bool:
    """Check if a file is parseable for code chunks."""
    parseable_extensions = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', 
        '.h', '.hpp', '.cs', '.go', '.rb', '.php', '.scala'
    }
    _, ext = os.path.splitext(filename.lower())
    return ext in parseable_extensions

def _detect_language(filename: str) -> str:
    """Detect programming language from file extension."""
    ext_to_lang = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'javascript',
        '.tsx': 'typescript',
        '.java': 'java',
        '.c': 'c',
        '.cpp': 'cpp',
        '.h': 'c',
        '.hpp': 'cpp',
        '.cs': 'csharp',
        '.go': 'go',
        '.rb': 'ruby',
        '.php': 'php',
        '.scala': 'scala',
        '.html': 'html',
        '.css': 'css',
        '.md': 'markdown',
        '.json': 'json',
        '.xml': 'xml',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.sql': 'sql',
    }
    
    _, ext = os.path.splitext(filename.lower())
    return ext_to_lang.get(ext, 'unknown') 