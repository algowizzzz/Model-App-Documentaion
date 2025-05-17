"""
End-to-end test script for the documentation summarization system.
This script processes a codebase through all summarization stages and generates organized output.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any
import logging # Import logging
import argparse # Import argparse
import sys
import traceback
import time

from src.data.loader import load_codebase, load_template
from src.summarization.engine import (
    generate_file_summary,
    generate_chunk_summary,
    generate_hierarchical_summary
)
from src.tools.core_tools import summarize_codebase_files
from src.prompts.base_prompts import prompt_outline_generation, create_section_drafting_prompt, prompt_code_manifest_generation
from src.utils.llm_factory import create_llm
from src.utils.config import Config

# Initialize LLM for direct calls (outline generation, section drafting)
config = Config()
llm = create_llm(
    model_name=config.get("llm.model_name", "claude-3-haiku-20240307"),  # Changed from sonnet to haiku for cost reduction
    temperature=config.get("llm.temperature", 0.1), # Slightly lower for more factual generation
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    # debugger=debugger, # Assuming debugger is available or handle appropriately
    mock_mode=config.get("llm.mock_mode", False) # Set to False for actual LLM calls
)

# Setup basic logging for the script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_output_directory() -> str:
    """Create timestamped output directory for test results."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join("output", f"summarization_test_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def write_json(data: Dict[str, Any], filepath: str) -> None:
    """Write dictionary data to a JSON file with pretty formatting."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def write_text(text: str, filepath: str) -> None:
    """Write text content to a file."""
    with open(filepath, 'w') as f:
        f.write(text)

def run_end_to_end_test(codebase_dir: str, template_path: str, max_retries: int = 3, retry_delay: int = 5) -> None:
    """Run the full end-to-end test of the summarization process."""
    # Create output directory with timestamp
    output_dir = create_output_directory()
    retry_count = 0
    last_error = None
    last_completed_step = "initialization"
    
    while retry_count <= max_retries:
        try:
            # Start from where we failed on retry
            logger.info(f"Running documentation generation{' (retry attempt '+str(retry_count)+')' if retry_count > 0 else ''}")
            
            # Initialize LLM (Claude via Anthropic client)
            anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not anthropic_api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable is not set. Please set it and try again.")
            
            # Create LLM with more robust error handling
            try:
                llm = create_llm(temperature=0.2)
                logger.info("LLM initialized successfully")
            except Exception as e:
                raise RuntimeError(f"Failed to initialize LLM: {str(e)}")
            
            if last_completed_step == "initialization":
                # Step 1: Load BMO documentation template
                logger.info("STEP 1: Loading BMO documentation template...")
                try:
                    with open(template_path, "r") as f:
                        template = json.load(f)
                    write_json(template, os.path.join(output_dir, "01_template.json"))
                    last_completed_step = "template_loading"
                    logger.info("STEP 1: ✓ BMO template loaded and saved.")
                except Exception as e:
                    raise RuntimeError(f"Failed to load template: {str(e)}")

            if last_completed_step == "template_loading":
                # Step 1b: Prepare placeholder Document Control metadata
                logger.info("STEP 1b: Preparing placeholder document control metadata...")
                doc_metadata_values = {
                    "doc_id": "MD-PFE-TRS-2025-001",
                    "model_name": codebase_dir, # Using codebase_dir as a placeholder
                    "model_version": "1.0.0",
                    "doc_version": "1.0d",
                    "status": "Draft",
                    "publication_date": datetime.now().strftime("%Y-%m-%d"),
                    "authors": ["BMO AI Documentation Assistant"],
                    "reviewers": ["[Reviewer Name(s) Placeholder]"],
                    "approver": "[Approver Name Placeholder]"
                }
                last_completed_step = "metadata_preparation"
                logger.info("STEP 1b: ✓ Placeholder document control metadata prepared.")

            if last_completed_step == "metadata_preparation":
                # Step 2: Generate detailed file summaries
                logger.info("STEP 2: Generating detailed file summaries...")
                try:
                    file_summaries = summarize_codebase_files(codebase_dir) 
                    summaries_dir = os.path.join(output_dir, "02_file_summaries")
                    os.makedirs(summaries_dir, exist_ok=True)
                    
                    logger.info(f"STEP 2: Saving {len(file_summaries)} file summaries...")
                    for file_path, summary in file_summaries.items():
                        safe_name = file_path.replace('/', '_').replace('\\', '_')
                        summary_path = os.path.join(summaries_dir, f"{safe_name}.txt")
                        write_text(summary, summary_path)
                    
                    all_summaries_content = "\n\n" + "="*80 + "\n\n".join(
                        f"File: {path}\n\n{summary}" for path, summary in file_summaries.items()
                    )
                    write_text(all_summaries_content, os.path.join(output_dir, "02_all_summaries.txt"))
                    last_completed_step = "file_summaries"
                    logger.info("STEP 2: ✓ Detailed file summaries generated and saved.")
                except Exception as e:
                    raise RuntimeError(f"Failed to generate file summaries: {str(e)}")

            if last_completed_step == "file_summaries":
                # Step 3: Generate hierarchical model summary using the updated prompt_hierarchical_summary
                logger.info("STEP 3: Generating hierarchical model summary...")
                hierarchical_summary_text = generate_hierarchical_summary(file_summaries)
                write_text(hierarchical_summary_text, os.path.join(output_dir, "03_hierarchical_summary.txt"))
                last_completed_step = "hierarchical_summary"
                logger.info("STEP 3: ✓ Hierarchical model summary generated and saved.")

            if last_completed_step == "hierarchical_summary":
                # Step 4: Generate detailed documentation outline using the updated prompt_outline_generation
                logger.info("STEP 4: Generating detailed documentation outline...")
                outline_prompt_input = {
                    "template": json.dumps(template), # Pass template as a JSON string
                    "codebase_summary": hierarchical_summary_text
                }
                ai_message_for_outline = llm.invoke(prompt_outline_generation.format_prompt(**outline_prompt_input).to_string())
                detailed_doc_outline_str = ai_message_for_outline.content
                
                try:
                    detailed_doc_outline_json = json.loads(detailed_doc_outline_str)
                    write_json(detailed_doc_outline_json, os.path.join(output_dir, "04_documentation_outline.json"))
                except json.JSONDecodeError:
                    write_text(detailed_doc_outline_str, os.path.join(output_dir, "04_documentation_outline.txt"))
                    logger.warning("Documentation outline was not valid JSON, saved as .txt")
                last_completed_step = "documentation_outline"
                logger.info("STEP 4: ✓ Detailed documentation outline generated and saved.")

            if last_completed_step == "documentation_outline":
                # Step 5: Generate full documentation draft using updated section drafting prompts
                logger.info("STEP 5: Generating full documentation draft...")
                full_documentation_draft = {
                    "template_name": template.get("name", "BMO Standard Model Documentation"),
                    "version": template.get("version", "1.0"),
                    "metadata_values": doc_metadata_values, # Add document control metadata
                    "sections": {}
                }
                
                num_sections = len(template.get("sections", []))
                for i, section_schema in enumerate(template.get("sections", [])):
                    section_id = section_schema["id"]
                    section_title = section_schema["title"]
                    logger.info(f"STEP 5: Drafting section {i+1}/{num_sections}: {section_title} (ID: {section_id})...")
                    
                    section_content_draft = "" 
                    
                    if section_schema.get("id") == "appendix_code_manifest" and section_schema.get("dynamic_content_source") == "file_summaries_list":
                        logger.info(f"    Using dynamic content generation for: {section_title}")
                        manifest_prompt_input = {
                            "file_summaries": json.dumps(file_summaries, indent=2) 
                        }
                        ai_message_manifest_draft = llm.invoke(prompt_code_manifest_generation.format_prompt(**manifest_prompt_input).to_string())
                        section_content_draft = ai_message_manifest_draft.content
                    else:
                        section_draft_input = {
                            "section_schema": json.dumps(section_schema), 
                            "detailed_outline_for_section": detailed_doc_outline_str, 
                            "hierarchical_model_summary": hierarchical_summary_text,
                            "relevant_file_summaries": json.dumps(file_summaries, indent=2) 
                        }
                        
                        drafting_prompt_template = create_section_drafting_prompt(section_id, section_title)
                        ai_message_section_draft = llm.invoke(drafting_prompt_template.format_prompt(**section_draft_input).to_string())
                        section_content_draft = ai_message_section_draft.content

                        # Add temporary file output to display content in monitor
                        temp_content_path = os.path.join(output_dir, f"draft_section_{section_id}.txt")
                        with open(temp_content_path, 'w') as f:
                            f.write(f"DRAFT SECTION: {section_title} (ID: {section_id})\n\n{section_content_draft}")
                        logger.info(f"    Section content written to: {temp_content_path}")

                        full_documentation_draft["sections"][section_id] = {
                            "title": section_title,
                            "content": section_content_draft,
                            "subsections": {}
                        }

                    if section_schema.get("subsections"):
                        num_subsections = len(section_schema.get("subsections", []))
                        for j, sub_section_schema in enumerate(section_schema.get("subsections", [])):
                            sub_section_id = sub_section_schema["id"]
                            sub_section_title = sub_section_schema["title"]
                            logger.info(f"    STEP 5: Drafting subsection {j+1}/{num_subsections}: {sub_section_title} (ID: {sub_section_id})...")
                            
                            sub_section_draft_input = {
                                "section_schema": json.dumps(sub_section_schema),
                                "detailed_outline_for_section": detailed_doc_outline_str, 
                                "hierarchical_model_summary": hierarchical_summary_text,
                                "relevant_file_summaries": json.dumps(file_summaries, indent=2) 
                            }
                            sub_drafting_prompt_template = create_section_drafting_prompt(sub_section_id, sub_section_title)
                            ai_message_subsection_draft = llm.invoke(sub_drafting_prompt_template.format_prompt(**sub_section_draft_input).to_string())
                            sub_section_content_draft = ai_message_subsection_draft.content

                            # Add temporary file output to display content in monitor
                            temp_subsection_path = os.path.join(output_dir, f"draft_subsection_{sub_section_id}.txt")
                            with open(temp_subsection_path, 'w') as f:
                                f.write(f"DRAFT SUBSECTION: {sub_section_title} (ID: {sub_section_id})\n\n{sub_section_content_draft}")
                            logger.info(f"        Subsection content written to: {temp_subsection_path}")

                            full_documentation_draft["sections"][section_id]["subsections"][sub_section_id] = {
                                "title": sub_section_title,
                                "content": sub_section_content_draft
                            }
                
                write_json(full_documentation_draft, os.path.join(output_dir, "05_full_documentation.json"))
                last_completed_step = "full_documentation"
                logger.info("STEP 5: ✓ Full documentation draft generated and saved.")

            if last_completed_step == "full_documentation":
                # Step 6: Generate summary report
                logger.info("STEP 6: Generating summary report...")
                report = {
                    "timestamp": datetime.now().isoformat(),
                    "codebase_directory": codebase_dir,
                    "template_used": template_path,
                    "files_processed": len(file_summaries),
                    "sections_generated": len(full_documentation_draft["sections"]),
                    "output_files": {
                        "template": "01_template.json",
                        "file_summaries": "02_file_summaries/",
                        "all_summaries": "02_all_summaries.txt",
                        "hierarchical_summary": "03_hierarchical_summary.txt",
                        "documentation_outline": "04_documentation_outline.json" if os.path.exists(os.path.join(output_dir, "04_documentation_outline.json")) else "04_documentation_outline.txt",
                        "full_documentation": "05_full_documentation.json",
                        "summary_report": "06_summary_report.json"
                    }
                }
                write_json(report, os.path.join(output_dir, "06_summary_report.json"))
                last_completed_step = "summary_report"
                logger.info("STEP 6: ✓ Summary report generated and saved.")

            logger.info(f"End-to-end test completed successfully! All outputs saved to: {output_dir}")
            return  # Success!

        except Exception as e:
            retry_count += 1
            last_error = e
            error_type = type(e).__name__
            error_msg = str(e)
            
            # Log the error
            logger.error(f"Error during {last_completed_step}: {error_type}: {error_msg}", exc_info=True)
            
            # Determine if this error is retryable
            retryable_errors = [
                "ConnectionError", "Timeout", "RequestError", "APIError", 
                "RateLimitError", "ServiceUnavailable", "AuthenticationError"
            ]
            retryable_error_messages = [
                "rate limit", "api usage limits", "too many requests", 
                "connection", "timeout", "temporary", "retry"
            ]
            
            is_retryable = (
                any(err_type in error_type for err_type in retryable_errors) or
                any(err_msg.lower() in error_msg.lower() for err_msg in retryable_error_messages)
            )
            
            if not is_retryable or retry_count > max_retries:
                # Not retryable or out of retries
                error_path = os.path.join(output_dir, "error_log.txt")
                detailed_error = f"""
ERROR DETAILS:
Time: {datetime.now().isoformat()}
Error type: {error_type}
Error message: {error_msg}
Last completed step: {last_completed_step}
Traceback:
{traceback.format_exc()}
                """
                write_text(detailed_error, error_path)
                logger.info(f"Error details saved to: {error_path}")
                
                if not is_retryable:
                    logger.error(f"Non-retryable error encountered. Stopping execution.")
                    break
                else:
                    logger.error(f"Max retries exceeded. Stopping execution.")
                    break
            else:
                # Retryable error, will retry
                logger.warning(f"Retryable error encountered during {last_completed_step}. "
                              f"Retry attempt {retry_count}/{max_retries} will begin in {retry_delay} seconds...")
                time.sleep(retry_delay)
                # Exponential backoff for retry delay
                retry_delay *= 2
    
    if last_error:
        error_path = os.path.join(output_dir, "error_log.txt")
        logger.error(f"Failed to complete the test after {retry_count - 1} retries. Last error: {str(last_error)}")
        logger.info(f"Error details saved to: {error_path}")
        
        # Suggestion for manual generation
        if os.path.exists(os.path.join(output_dir, "05_full_documentation.json")):
            logger.info("The documentation JSON appears to have been generated. You can try running:")
            logger.info(f"  python generate_final_documentation.py --json-input-dir {output_dir} --template-path {template_path}")
        
        raise RuntimeError(f"Failed to complete after {retry_count - 1} retries: {str(last_error)}")

if __name__ == "__main__":
    # --- Original Configuration (kept for reference or if no CLI args provided) ---
    # CODEBASE_DIR = "MonteCarloPFE"
    # TEMPLATE_PATH = "templates/bmo_model_documentation_template.json"

    parser = argparse.ArgumentParser(description="Run end-to-end documentation summarization.")
    parser.add_argument("--codebase-dir", type=str, required=True,
                        help="Directory containing the codebase to summarize.")
    parser.add_argument("--template-path", type=str, required=True,
                        help="Path to the BMO documentation template file to use.")
    
    args = parser.parse_args()

    logger.info("="*80)
    logger.info("Starting End-to-End BMO Summarization Test with Enhanced Logging")
    logger.info(f"Codebase Directory: {args.codebase_dir}")
    logger.info(f"Template Path: {args.template_path}")
    logger.info("="*80)
    
    run_end_to_end_test(args.codebase_dir, args.template_path) 