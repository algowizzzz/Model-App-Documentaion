"""
Generates the final Markdown documentation from the JSON output of test_end_to_end_summarization.py
"""
import json
import os
from datetime import datetime
import argparse # Import argparse
from typing import Dict, Any, List # Ensure List is imported

# --- Configuration ---
# JSON_INPUT_DIR = "output/summarization_test_20250517_132402"  # Overridden by CLI arg
# TEMPLATE_PATH = "templates/bmo_model_documentation_template.json" # Overridden by CLI arg
OUTPUT_MARKDOWN_FILE = "final_documentation.md" 

# METADATA_TABLE_ORDER is dynamically determined from the template later

def load_json_data(filepath: str) -> Dict[str, Any]:
    """Load data from a JSON file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        raise
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {filepath}")
        raise

def generate_table_of_contents(sections_data: Dict[str, Any], level: int = 1) -> str:
    """Generate a markdown table of contents from sections data."""
    toc = []
    for section_id, section_details in sections_data.items():
        title = section_details.get("title", "Untitled Section")
        # Create a simple anchor link (GitHub-style: lowercase, spaces to dashes)
        anchor = title.lower().replace(" ", "-").replace("[", "").replace("]", "").replace("(", "").replace(")", "").replace(".", "")
        toc.append(f"{'  ' * (level - 1)}- [{title}](#{anchor})")
        if "subsections" in section_details and section_details["subsections"]:
            toc.append(generate_table_of_contents(section_details["subsections"], level + 1))
    return "\n".join(toc)

def format_section_content(section_data: Dict[str, Any], level: int = 2) -> str:
    """Format the content of a single section or subsection for Markdown."""
    content = []
    title = section_data.get("title", "Untitled Section")
    section_content = section_data.get("content", "No content provided.")
    
    content.append(f"{'#' * level} {title}\n")
    content.append(f"{section_content}\n")
    
    if "subsections" in section_data and section_data["subsections"]:
        for sub_id, sub_details in section_data["subsections"].items():
            content.append(format_section_content(sub_details, level + 1))
            
    return "\n".join(content)

def main(json_input_dir: str, template_path: str):
    """Load data, generate markdown, and write to file."""
    print(f"Starting final documentation generation...")
    print(f"Reading JSON inputs from: {json_input_dir}")
    print(f"Using template from: {template_path}")

    try:
        full_doc_path = os.path.join(json_input_dir, "05_full_documentation.json")
        template_data_path = template_path # Already the full path
        report_path = os.path.join(json_input_dir, "06_summary_report.json")

        full_doc = load_json_data(full_doc_path)
        template_data = load_json_data(template_data_path)
        report_data = load_json_data(report_path)
        
    except Exception as e:
        print(f"Failed to load necessary JSON files: {e}")
        return

    markdown_parts = []

    # 1. Title and Generation Info
    markdown_parts.append(f"# Code Documentation\n")
    markdown_parts.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    codebase_name = report_data.get("codebase_directory", "Unknown Codebase")
    markdown_parts.append(f"Codebase: `{codebase_name}`\n")

    # 2. Table of Contents
    markdown_parts.append(f"## Table of Contents\n")
    # Use template sections for TOC structure to ensure it matches the intended order and hierarchy
    template_sections_for_toc = {}
    if "sections" in template_data:
        for sec_template in template_data["sections"]:
            sec_id = sec_template["id"]
            template_sections_for_toc[sec_id] = {
                "title": sec_template["title"],
                "subsections": {}
            }
            if "subsections" in sec_template:
                for sub_sec_template in sec_template["subsections"]:
                    sub_sec_id = sub_sec_template["id"]
                    template_sections_for_toc[sec_id]["subsections"][sub_sec_id] = {
                        "title": sub_sec_template["title"]
                    }
    
    toc_content = generate_table_of_contents(template_sections_for_toc)
    markdown_parts.append(f"{toc_content}\n")

    # 3. Document Control Table (from template structure and 05_full_documentation metadata_values)
    markdown_parts.append(f"## Document Control\n")
    metadata_table_order = []
    if "metadata_fields" in template_data:
        metadata_table_order = [field["id"] for field in template_data["metadata_fields"]]
    
    if metadata_table_order and "metadata_values" in full_doc:
        headers = ["Property", "Value"]
        table_rows = [f"| {' | '.join(headers)} |", f"| {' | '.join(['---'] * len(headers))} |"]
        doc_metadata_values = full_doc["metadata_values"]
        
        for key in metadata_table_order:
            # Find the field label from template_data based on id
            field_label = key
            for field_def in template_data.get("metadata_fields", []):
                if field_def.get("id") == key:
                    field_label = field_def.get("label", key)
                    break
            
            value = str(doc_metadata_values.get(key, "Not Provided"))
            table_rows.append(f"| {field_label} | {value} |")
        markdown_parts.append("\n".join(table_rows) + "\n")
    else:
        markdown_parts.append("Document control information not available or template misconfigured.\n")

    # 4. Run Metadata Table (from 06_summary_report.json)
    markdown_parts.append(f"## Run Metadata\n")
    if report_data:
        headers = ["Property", "Value"]
        table_rows = [f"| {' | '.join(headers)} |", f"| {' | '.join(['---'] * len(headers))} |"]
        run_metadata_to_display = {
            "Files Processed": report_data.get("files_processed", "N/A"),
            "Sections Generated (from template)": report_data.get("sections_generated", "N/A"),
            "Template Used": report_data.get("template_used", "N/A"),
        }
        for key, value in run_metadata_to_display.items():
            table_rows.append(f"| {key} | {value} |")
        markdown_parts.append("\n".join(table_rows) + "\n")
    else:
        markdown_parts.append("Run metadata not available.\n")

    # 5. Main Content Sections (from 05_full_documentation.json, structured by template order)
    if "sections" in template_data:
        for section_template in template_data["sections"]:
            section_id = section_template["id"]
            if section_id in full_doc.get("sections", {}):
                section_data_from_doc = full_doc["sections"][section_id]
                # Ensure title comes from template for consistency, but content from doc
                section_to_format = {
                    "title": section_template["title"],
                    "content": section_data_from_doc.get("content", "Content not generated."),
                    "subsections": {}
                }
                
                # Process subsections, ensuring their order and titles also come from template
                if "subsections" in section_template and "subsections" in section_data_from_doc:
                    for sub_section_template in section_template["subsections"]:
                        sub_section_id = sub_section_template["id"]
                        if sub_section_id in section_data_from_doc["subsections"]:
                            sub_section_data_from_doc = section_data_from_doc["subsections"][sub_section_id]
                            section_to_format["subsections"][sub_section_id] = {
                                "title": sub_section_template["title"],
                                "content": sub_section_data_from_doc.get("content", "Content not generated.")
                            }
                
                markdown_parts.append(format_section_content(section_to_format, level=2))
            else:
                 markdown_parts.append(f"## {section_template['title']}\n\nContent for this section (ID: {section_id}) was not found in the generated documentation.\n")

    # Write to file
    output_filepath = os.path.join(json_input_dir, OUTPUT_MARKDOWN_FILE)
    try:
        with open(output_filepath, 'w') as f:
            f.write("\n".join(markdown_parts))
        print(f"Successfully generated Markdown documentation at: {output_filepath}")
    except IOError as e:
        print(f"Error writing Markdown file: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate final documentation from processed summaries.")
    parser.add_argument("--json-input-dir", type=str, required=True, 
                        help="Path to the directory containing 05_full_documentation.json and 06_summary_report.json.")
    parser.add_argument("--template-path", type=str, required=True, 
                        help="Path to the BMO documentation template JSON file.")
    args = parser.parse_args()
    main(args.json_input_dir, args.template_path) 