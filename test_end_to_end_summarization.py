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

def run_end_to_end_test(codebase_dir: str, template_path: str) -> None:
    """
    Run end-to-end test of the BMO-standard summarization system.
    Args:
        codebase_dir: Directory containing the codebase to summarize
        template_path: Path to the BMO documentation template file to use
    """
    output_dir = create_output_directory()
    logger.info(f"Output will be saved to: {output_dir}")

    try:
        # Step 1: Load BMO documentation template
        logger.info("STEP 1: Loading BMO documentation template...")
        template = load_template(template_path)
        write_json(template, os.path.join(output_dir, "01_template.json"))
        logger.info("STEP 1: ✓ BMO template loaded and saved.")

        # Step 1b: Prepare placeholder Document Control metadata (example)
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
        logger.info("STEP 1b: ✓ Placeholder document control metadata prepared.")

        # Step 2: Generate detailed file summaries using the updated prompt_file_summary (via summarize_codebase_files tool)
        logger.info("STEP 2: Generating detailed file summaries...")
        # summarize_codebase_files tool already uses the updated prompt_file_summary
        # It internally logs file processing, so we don't need to re-log each file here explicitly
        # unless we want to add a counter like "Processing file X of Y"
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
        logger.info("STEP 2: ✓ Detailed file summaries generated and saved.")

        # Step 3: Generate hierarchical model summary using the updated prompt_hierarchical_summary
        logger.info("STEP 3: Generating hierarchical model summary...")
        hierarchical_summary_text = generate_hierarchical_summary(file_summaries)
        write_text(hierarchical_summary_text, os.path.join(output_dir, "03_hierarchical_summary.txt"))
        logger.info("STEP 3: ✓ Hierarchical model summary generated and saved.")

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
        logger.info("STEP 4: ✓ Detailed documentation outline generated and saved.")

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
        logger.info("STEP 5: ✓ Full documentation draft generated and saved.")

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
        logger.info("STEP 6: ✓ Summary report generated and saved.")

        logger.info(f"End-to-end test completed successfully! All outputs saved to: {output_dir}")

    except Exception as e:
        error_msg = f"Error during end-to-end test: {str(e)}"
        # Ensure output_dir is defined even if error occurs early
        if 'output_dir' not in locals():
            output_dir = "output/error_run" # Fallback
            os.makedirs(output_dir, exist_ok=True)
            
        error_path = os.path.join(output_dir, "error_log.txt")
        # Log error using logger and also write to file
        logger.error(error_msg, exc_info=True) # exc_info=True will log stack trace
        write_text(f"{datetime.now().isoformat()} - {error_msg}\n{traceback.format_exc() if sys.exc_info()[0] else ''}", error_path)
        logger.info(f"Error details also saved to: {error_path}")
        # No raise here, allow script to finish if possible to facilitate debugging via logs
        # Or re-raise if you want the script to terminate with an error status
        # raise 

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
    run_end_to_end_test(CODEBASE_DIR, TEMPLATE_PATH) 