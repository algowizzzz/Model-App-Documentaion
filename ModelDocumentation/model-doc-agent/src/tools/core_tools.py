from typing import List, Dict, Any, Union, cast
from langchain.tools import Tool, tool
from langchain.chains import LLMChain
import os
import sys

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

# Initialize LLM, Config, and Debugger
# These would typically be managed by the application context or dependency injection
config = Config()
debugger = ModelDocDebugger(logger_name="CoreTools", debug_level=config.get("debug_level", "INFO"))
llm = create_llm(debugger=debugger) # Pass debugger to llm_factory if it accepts it

# --- Refactored Tool Helper Functions (with error handling and debugging) ---

@debugger.time_function
def _summarize_single_file_content(file_name: str, file_content: str, prompt: PromptTemplate) -> str:
    """Helper to summarize content of a single file using a provided prompt."""
    debugger.logger.debug(f"Attempting to summarize: {file_name}")
    if not file_content.strip():
        debugger.logger.info(f"Skipping empty file content for: {file_name}")
        return "File content is empty or contains no summarizable text."
    try:
        chain = LLMChain(llm=llm, prompt=prompt)
        # Ensure correct variable name for the prompt is used, e.g. "file_content"
        # The base_prompts.py uses "file_content" for prompt_file_summary
        summary = chain.invoke({"file_content": file_content})["text"]
        debugger.logger.debug(f"Generated summary for {file_name} (length: {len(summary)})")
        return summary
    except Exception as e:
        debugger.log_exception("_summarize_single_file_content", e, {"file_name": file_name})
        return f"Error summarizing file {file_name}: {str(e)}"

@tool("summarize_codebase_files")
@debugger.time_function
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

@tool("generate_hierarchical_summary")
@debugger.time_function
def generate_hierarchical_summary(file_summaries: Dict[str, str]) -> str:
    """
    Creates a single, high-level hierarchical summary from a dictionary of individual file summaries.
    This tool is useful for understanding the overall architecture or purpose of a collection of code files.
    Input:
        file_summaries (Dict[str, str]): A dictionary where keys are file paths or names
                                         and values are their textual summaries.
    Output:
        str: A string containing the consolidated hierarchical summary.
             Returns an error message string if input is invalid or summarization fails.
    """
    debugger.logger.info(f"Starting hierarchical summary generation for {len(file_summaries)} summaries.")
    if not isinstance(file_summaries, dict) or not file_summaries:
        msg = "Input must be a non-empty dictionary of file summaries."
        debugger.logger.error(msg)
        return f"Error: {msg}"

    # Format summaries for the prompt
    valid_summaries = {fn: sm for fn, sm in file_summaries.items() if isinstance(sm, str) and sm.strip() and not sm.startswith("Error:") and not sm.startswith("File is empty")}
    
    if not valid_summaries:
        msg = "No valid summaries provided for hierarchical summarization. Please ensure individual file summaries were generated successfully."
        debugger.logger.warning(msg)
        return msg

    formatted_summaries = "\n\n".join([
        f"File: {str(fn)}\nSummary:\n{str(sm)}\n---"
        for fn, sm in valid_summaries.items()
    ])
    
    try:
        chain = LLMChain(llm=llm, prompt=prompt_hierarchical_summary)
        # The prompt_hierarchical_summary expects "summaries"
        hier_summary_result = chain.invoke({"summaries": formatted_summaries})
        hier_summary = hier_summary_result.get("text", "") if isinstance(hier_summary_result, dict) else str(hier_summary_result)

        debugger.logger.info("Successfully generated hierarchical summary.")
        return hier_summary
    except Exception as e:
        debugger.log_exception("generate_hierarchical_summary", e, {"num_summaries": len(valid_summaries)})
        return f"Error generating hierarchical summary: {str(e)}"

@tool("generate_documentation_outline_from_template")
@debugger.time_function
def generate_documentation_outline_from_template(template_path: str) -> str:
    """
    Generates a draft documentation outline based on a provided JSON documentation template file.
    The template should define the structure and sections of the desired documentation.
    Input:
        template_path (str): The file path to the JSON documentation template.
    Output:
        str: A string representing the generated documentation outline.
             Returns an error message string if the template is not found, is invalid, or outline generation fails.
    """
    debugger.logger.info(f"Starting outline generation for template: {template_path}")
    try:
        template_data = load_template(template_path) # load_template now returns dict or raises error
        sections = template_data.get("sections", [])
        if not sections:
            msg = "No sections found in the template. The template must have a 'sections' list."
            debugger.logger.warning(msg)
            return f"Warning: {msg}"

        # Format sections for the prompt_outline_generation
        # The prompt expects "template_sections"
        sections_str = "\n\n".join([
            f"Section Title: {s.get('title', 'Untitled Section')}\nID: {s.get('id', 'N/A')}\nDescription: {s.get('description', 'No description')}\n---"
            for s in sections if isinstance(s, dict)
        ])
        
        if not sections_str.strip():
            msg = "Template sections are empty or improperly formatted."
            debugger.logger.warning(msg)
            return f"Warning: {msg}"

        chain = LLMChain(llm=llm, prompt=prompt_outline_generation)
        outline_result = chain.invoke({"template_sections": sections_str})
        outline = outline_result.get("text", "") if isinstance(outline_result, dict) else str(outline_result)
        debugger.logger.info(f"Successfully generated outline for template: {template_path}")
        return outline
    except FileNotFoundError: # Handled by load_template or os error if not caught by loader
        debugger.logger.error(f"Template file not found: {template_path}")
        return f"Error: Template file not found at {template_path}"
    except ValueError as ve: # If load_template returns error string or raises ValueError for JSON issues
        debugger.logger.error(f"Invalid template structure for {template_path}: {ve}")
        return f"Error: Invalid template structure in {template_path}. {str(ve)}"
    except Exception as e:
        debugger.log_exception("generate_documentation_outline_from_template", e, {"template_path": template_path})
        return f"Error generating outline for {template_path}: {str(e)}"

@tool("draft_documentation_section_from_template")
@debugger.time_function
def draft_documentation_section_from_template(
    template_path: str, 
    section_id: str, # Changed to str for flexibility, template IDs are often strings
    contextual_information: str # Renamed from code_summaries_and_snippets for clarity
) -> str:
    """
    Generates a draft for a specific section of the documentation, identified by its ID in the template.
    It uses the provided contextual information (e.g., code summaries, relevant code snippets, hierarchical summaries)
    to tailor the draft to the section's purpose as defined in the documentation template.
    
    Input:
        template_path (str): The file path to the JSON documentation template.
        section_id (str): The 'id' of the target section within the template's 'sections' list.
        contextual_information (str): A string containing all relevant information (e.g., file summaries,
                                     code snippets, hierarchical summary) needed to draft this section.
                                     This should be carefully prepared by the agent.
    Output:
        str: The drafted content for the specified documentation section.
             Returns an error message string if the template or section is not found, or drafting fails.
    """
    debugger.logger.info(f"Starting draft for section ID '{section_id}' from template: {template_path}")
    try:
        template_data = load_template(template_path)
        target_section = None
        for sec in template_data.get("sections", []):
            if isinstance(sec, dict) and sec.get("id") == section_id:
                target_section = sec
                break
        
        if not target_section:
            msg = f"Section with ID '{section_id}' not found in template {template_path}."
            debugger.logger.error(msg)
            # List available section IDs for easier debugging by the agent/user
            available_ids = [str(s.get("id")) for s in template_data.get("sections", []) if isinstance(s, dict) and "id" in s]
            return f"Error: {msg} Available section IDs: {', '.join(available_ids) if available_ids else 'None'}"

        section_title = target_section.get("title", "Untitled Section")
        section_description = target_section.get("description", "No specific description provided.")
        
        # Get the specific prompt for this section using the factory from base_prompts
        # create_section_drafting_prompt expects section_title and section_guidance
        section_draft_prompt = create_section_drafting_prompt(section_title, section_description)
        
        chain = LLMChain(llm=llm, prompt=section_draft_prompt)
        # The prompt generated by create_section_drafting_prompt expects "contextual_information"
        draft_result = chain.invoke({"contextual_information": contextual_information})
        draft = draft_result.get("text", "") if isinstance(draft_result, dict) else str(draft_result)

        debugger.logger.info(f"Successfully drafted section '{section_title}' (ID: {section_id}).")
        return draft
    except FileNotFoundError:
        debugger.logger.error(f"Template file not found: {template_path}")
        return f"Error: Template file not found at {template_path}"
    except ValueError as ve: # If load_template returns error string or raises ValueError for JSON issues
        debugger.logger.error(f"Invalid template structure for {template_path}: {ve}")
        return f"Error: Invalid template structure in {template_path}. {str(ve)}"
    except Exception as e:
        debugger.log_exception("draft_documentation_section_from_template", e, 
                               {"template_path": template_path, "section_id": section_id})
        return f"Error drafting section ID '{section_id}': {str(e)}"

@tool("suggest_documentation_improvements")
@debugger.time_function
def suggest_documentation_improvements(
    documentation_draft: str, 
    code_summaries: Dict[str, str], # Kept as dict for structured input
    hierarchical_summary: str = ""  # Optional, but can be very useful context
) -> str:
    """
    Reviews a draft of the documentation along with code summaries (and an optional hierarchical summary)
    to provide suggestions for improvement. It focuses on clarity, completeness, accuracy, and consistency.
    
    Input:
        documentation_draft (str): The current draft of the documentation to be reviewed.
        code_summaries (Dict[str, str]): A dictionary of summaries for relevant code files (path -> summary).
        hierarchical_summary (str, optional): An overall summary of the codebase. Defaults to "".
    Output:
        str: A string containing actionable suggestions for improving the documentation.
             Returns an error message string if the review process fails.
    """
    debugger.logger.info(f"Starting suggestion of improvements for documentation draft (length: {len(documentation_draft)}).")
    
    if not documentation_draft.strip():
        msg = "Documentation draft is empty. Cannot provide suggestions."
        debugger.logger.warning(msg)
        return f"Warning: {msg}"

    # Format code summaries for the prompt
    formatted_summaries = "\n\n".join([
        f"File: {str(fn)}\nSummary:\n{str(sm)}\n---"
        for fn, sm in code_summaries.items()
        if isinstance(sm, str) and sm.strip() and not sm.startswith("Error:")
    ])

    if not formatted_summaries and not hierarchical_summary:
        msg = "No code summaries or hierarchical summary provided. Suggestions may be limited."
        debugger.logger.warning(msg)
        # Proceed, but with a warning, as the LLM might still offer generic advice based on the draft alone.
    
    # The prompt_improvement_suggestions expects "documentation_draft", "code_context"
    # We will combine formatted_summaries and hierarchical_summary into "code_context"
    code_context = formatted_summaries
    if hierarchical_summary.strip():
        code_context = f"Hierarchical Summary:\n{hierarchical_summary}\n\n--- Code File Summaries ---\n{formatted_summaries}" if formatted_summaries else f"Hierarchical Summary:\n{hierarchical_summary}"

    if not code_context.strip(): # If both were empty
        code_context = "No specific code context (summaries or hierarchical summary) was provided for this review."


    try:
        chain = LLMChain(llm=llm, prompt=prompt_improvement_suggestions)
        suggestions_result = chain.invoke({
            "documentation_draft": documentation_draft,
            "code_context": code_context
        })
        suggestions = suggestions_result.get("text", "") if isinstance(suggestions_result, dict) else str(suggestions_result)
        debugger.logger.info("Successfully generated improvement suggestions.")
        return suggestions
    except Exception as e:
        debugger.log_exception("suggest_documentation_improvements", e, 
                               {"draft_length": len(documentation_draft), "num_summaries": len(code_summaries)})
        return f"Error suggesting improvements: {str(e)}"

# List of all tools available for the agent
TOOLS: List[Tool] = [
    cast(Tool, summarize_codebase_files),
    cast(Tool, generate_hierarchical_summary),
    cast(Tool, generate_documentation_outline_from_template),
    cast(Tool, draft_documentation_section_from_template),
    cast(Tool, suggest_documentation_improvements),
]

# Example of how to manually create a Tool if not using @tool decorator
# (This is for illustration; @tool is preferred)
# summarize_codebase_files_tool = Tool(
# name="summarize_codebase_files",
# func=summarize_codebase_files,
# description=(
# "Loads all code files from a specified directory, generates a textual summary for each file, "
# "and returns a dictionary mapping file paths to their summaries. "
# "Handles various file types and intelligently extracts textual content. "
# "Input: code_dir (str). Output: Dict[str, str] of file_path -> summary."
# )
# ) 