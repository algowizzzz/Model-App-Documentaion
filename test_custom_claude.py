#!/usr/bin/env python3
"""
Test script for using custom templates with the documentation agent.
"""
import os
import sys
from dotenv import load_dotenv
import traceback

# Load environment variables from .env file
load_dotenv()

# Add the root directory to the path
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Import our custom Claude agent implementation
from src.utils.claude_agent import create_claude_agent
from langchain.tools import tool
from src.data.loader import load_codebase, load_template
from src.summarization.engine import (
    generate_file_summary,
    generate_chunk_summary,
    generate_hierarchical_summary
)
from src.tools.core_tools import summarize_codebase_files

print("-" * 80)
print("CUSTOM CLAUDE AGENT TEST")
print("-" * 80)

# Create some simple test tools
@tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers together."""
    return a * b

@tool
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b

# Define tools list
tools = [multiply, add]

# Check for the API key
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    print("Error: ANTHROPIC_API_KEY environment variable is not set.")
    sys.exit(1)

try:
    print("\nInitializing custom Claude agent...")
    agent = create_claude_agent(
        tools=tools,
        model_name="claude-3-opus-20240229",
        temperature=0.2,
        verbose=True
    )
    
    print("\nAgent initialized successfully!\n")
    
    # Test the agent with a tool-requiring query
    query = "What is 15 multiplied by 7, and then that result added to 32?"
    print(f"Testing with query: '{query}'")
    
    response = agent.invoke({"input": query})
    print(f"\nFinal answer: {response.get('output', 'No output')}")
    
except Exception as e:
    print(f"Error: {str(e)}")
    traceback.print_exc()

print("\n" + "-" * 80)
print("TEST COMPLETE")
print("-" * 80)

def write_to_output(text: str, file_handle):
    """Helper function to write to both console and file."""
    print(text)
    file_handle.write(text + "\n")

def test_custom_template_summarization():
    """Test summarization using custom template."""
    
    with open("custom_template_output.txt", "w") as output_file:
        write_to_output("=== Starting Custom Template Summarization ===\n", output_file)
        
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
        write_to_output("\n=== Hierarchical Summary ===\n", output_file)
        hierarchical_summary = generate_hierarchical_summary(file_summaries)
        write_to_output(hierarchical_summary, output_file)
        
        # Step 3: Load and use custom template
        write_to_output("\n=== Custom Template Structure ===\n", output_file)
        template = load_template("templates/custom_summary_template.json")
        write_to_output("Template sections:", output_file)
        for section in template["sections"]:
            write_to_output(f"\n- {section['title']}", output_file)
            if "subsections" in section:
                for subsection in section["subsections"]:
                    write_to_output(f"  * {subsection['title']}", output_file)
        
        write_to_output("\n=== Custom Template Summarization Completed ===", output_file)

if __name__ == "__main__":
    test_custom_template_summarization() 