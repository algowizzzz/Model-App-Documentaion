"""
Test script for demonstrating cross-codebase summarization.
"""

from src.tools.core_tools import summarize_codebase_files
from src.summarization.engine import generate_hierarchical_summary

def write_to_output(text: str, file_handle):
    """Helper function to write to both console and file."""
    print(text)
    file_handle.write(text + "\n")

def test_codebase_summarization():
    """Test summarization across the entire codebase."""
    
    with open("codebase_summary_output.txt", "w") as output_file:
        write_to_output("=== Starting Codebase Summarization ===\n", output_file)
        
        # Step 1: Generate summaries for all files
        write_to_output("Generating summaries for all files...\n", output_file)
        file_summaries = summarize_codebase_files("test_codebase")
        
        # Print individual file summaries
        write_to_output("\n=== Individual File Summaries ===\n", output_file)
        for file_path, summary in file_summaries.items():
            write_to_output(f"\nFile: {file_path}", output_file)
            write_to_output("-" * 80, output_file)
            write_to_output(summary, output_file)
            write_to_output("-" * 80 + "\n", output_file)
        
        # Step 2: Generate hierarchical summary
        write_to_output("\n=== Hierarchical Codebase Summary ===\n", output_file)
        hierarchical_summary = generate_hierarchical_summary(file_summaries)
        write_to_output(hierarchical_summary, output_file)
        
        write_to_output("\n=== Codebase Summarization Completed ===", output_file)

if __name__ == "__main__":
    test_codebase_summarization() 