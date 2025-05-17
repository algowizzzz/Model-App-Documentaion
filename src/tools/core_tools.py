from typing import List, Dict, Any, Union, cast
from langchain.tools import Tool, tool
from langchain.chains import LLMChain
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add path context for absolute imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, ".."))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Use absolute imports
from src.utils.llm_factory import create_llm
from src.utils.config import Config
from src.debug.logger import ModelDocDebugger
from src.data.loader import load_codebase, load_template
from src.data.schema import ParsedFile
from src.prompts.base_prompts import (
    prompt_file_summary, prompt_hierarchical_summary, prompt_outline_generation,
    create_section_drafting_prompt, prompt_improvement_suggestions, PromptTemplate
) 

# Initialize config and debugger for tools
config = Config()
debugger = ModelDocDebugger(logger_name="CoreTools", debug_level="INFO")

def _summarize_single_file_content(file_path: str, content: str, prompt_template: PromptTemplate) -> str:
    """Helper function to summarize a single file's content using the provided prompt template."""
    try:
        llm = create_llm(
            model_name=config.get("llm.model_name", "claude-3-opus-20240229"),
            temperature=config.get("llm.temperature", 0.2),
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            debugger=debugger,
            mock_mode=config.get("llm.mock_mode", True)
        )
        chain = LLMChain(llm=llm, prompt=prompt_template)
        return chain.run(file_path=file_path, content=content)
    except Exception as e:
        debugger.log_exception("_summarize_single_file_content", e, {"file_path": file_path})
        return f"Error summarizing {file_path}: {str(e)}"

@tool("summarize_codebase_files")
def summarize_codebase_files(code_dir: str) -> Dict[str, str]:
    """
    Loads all code files from a specified directory, generates a textual summary for each file,
    and returns a dictionary mapping file paths to their summaries.
    This tool handles various file types and intelligently extracts textual content for summarization.
    It uses the 'prompt_file_summary' for generating individual file summaries.
    Input:
        code_dir (str): The directory path containing the code files to be summarized.
    Output:
        Dict[str, str]: A dictionary where keys are file paths (relative to `code_dir`)
                        and values are their corresponding textual summaries.
                        Returns {"error": "message"} if a major error occurs during loading or processing.
    """
    debugger.logger.info(f"Starting summarize_codebase_files for directory: {code_dir}")
    try:
        # Load codebase, parse_chunks can be True if downstream tasks need chunks,
        # but for summarization, full_content is used.
        files_data = load_codebase(code_dir, parse_chunks=config.get("parser.parse_chunks", True))
        
        summaries: Dict[str, str] = {}
        if not files_data:
            debugger.logger.warning(f"No files found or loaded from directory: {code_dir}")
            return {"info": f"No files found or loaded from directory: {code_dir}"}

        for file_path_rel, data_item in files_data.items():
            content_to_summarize = ""
            if isinstance(data_item, ParsedFile):
                content_to_summarize = data_item.full_content
                debugger.logger.debug(f"Summarizing ParsedFile: {file_path_rel} using its full content.")
            elif isinstance(data_item, str): # Handles non-Python files or files not parsed into ParsedFile
                content_to_summarize = data_item
                debugger.logger.debug(f"Summarizing raw file content: {file_path_rel}")
            else:
                debugger.logger.warning(f"Skipping unsupported data type for file {file_path_rel}: {type(data_item)}")
                summaries[file_path_rel] = "Error: Unsupported file data type for summarization."
                continue
            
            summaries[file_path_rel] = _summarize_single_file_content(file_path_rel, content_to_summarize, prompt_file_summary)
        
        debugger.logger.info(f"Successfully generated summaries for {len(summaries)} files.")
        return summaries
    except Exception as e:
        debugger.log_exception("summarize_codebase_files", e, {"code_dir": code_dir})
        return {"error": f"Failed to summarize files in {code_dir}: {str(e)}"}

# Define the tools list available for the agent
TOOLS = [
    summarize_codebase_files
] 