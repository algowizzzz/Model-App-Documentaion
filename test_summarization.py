"""
Test script for verifying the summarization functionality.
"""

from src.data.loader import load_codebase
from src.data.schema import ParsedFile, CodeChunk
from src.summarization.engine import (
    generate_file_summary,
    generate_chunk_summary,
    generate_hierarchical_summary
)

def write_to_output(text: str, file_handle):
    """Helper function to write to both console and file."""
    print(text)
    file_handle.write(text + "\n")

def test_file_level_summary(output_file):
    """Test generation of file-level summaries."""
    write_to_output("\n=== Testing File-Level Summarization ===", output_file)
    
    # Load test files
    result = load_codebase("test_codebase", parse_chunks=True)
    complex_file = result["complex_module.py"]
    
    # Generate file summary
    write_to_output("\n--- Complex Module Summary ---", output_file)
    summary = generate_file_summary(complex_file)
    write_to_output(f"Summary length: {len(summary)}", output_file)
    write_to_output("Summary: " + summary, output_file)
    
    # Verify summary content
    assert "risk calculation" in summary.lower(), "Summary should mention main purpose"
    assert "RiskCalculator" in summary, "Summary should mention main class"
    assert "RiskFactor" in summary, "Summary should mention supporting class"
    write_to_output("File summary content verification passed", output_file)

def test_chunk_level_summary(output_file):
    """Test generation of chunk-level summaries."""
    write_to_output("\n=== Testing Chunk-Level Summarization ===", output_file)
    
    # Load test files
    result = load_codebase("test_codebase", parse_chunks=True)
    complex_file = result["complex_module.py"]
    
    # Test class summary
    write_to_output("\n--- Class Summary ---", output_file)
    risk_calculator = next(chunk for chunk in complex_file.chunks if chunk.name == "RiskCalculator")
    class_summary = generate_chunk_summary(risk_calculator)
    write_to_output(f"Class summary length: {len(class_summary)}", output_file)
    write_to_output("Class summary: " + class_summary, output_file)
    
    # Test method summary
    write_to_output("\n--- Method Summary ---", output_file)
    calculate_risk = next(
        method for method in risk_calculator.metadata["methods"] 
        if method.name == "calculate_total_risk"
    )
    method_summary = generate_chunk_summary(calculate_risk)
    write_to_output(f"Method summary length: {len(method_summary)}", output_file)
    write_to_output("Method summary: " + method_summary, output_file)
    
    # Verify summaries
    assert "risk" in class_summary.lower(), "Class summary should mention purpose"
    assert "calculate" in method_summary.lower(), "Method summary should mention functionality"
    write_to_output("Chunk summary content verification passed", output_file)

def test_hierarchical_summary(output_file):
    """Test generation of hierarchical summaries."""
    write_to_output("\n=== Testing Hierarchical Summarization ===", output_file)
    
    # Load test files
    result = load_codebase("test_codebase", parse_chunks=True)
    complex_file = result["complex_module.py"]
    
    # Generate hierarchical summary
    write_to_output("\n--- Hierarchical Summary ---", output_file)
    hierarchy = generate_hierarchical_summary(complex_file)
    
    # Verify structure
    assert "file_summary" in hierarchy, "Should have file-level summary"
    assert "classes" in hierarchy, "Should have class summaries"
    assert "functions" in hierarchy, "Should have function summaries"
    
    # Print summary structure and content
    write_to_output("\nSummary Structure and Content:", output_file)
    write_to_output("\nFile Summary:", output_file)
    write_to_output(hierarchy['file_summary'], output_file)
    
    write_to_output("\nClass Summaries:", output_file)
    for cls in hierarchy['classes']:
        write_to_output(f"\nClass: {cls['name']}", output_file)
        write_to_output(f"Summary: {cls['summary']}", output_file)
        write_to_output("\nMethods:", output_file)
        for method in cls['methods']:
            write_to_output(f"\n  Method: {method['name']}", output_file)
            write_to_output(f"  Summary: {method['summary']}", output_file)
    
    write_to_output("\nFunction Summaries:", output_file)
    for func in hierarchy['functions']:
        write_to_output(f"\nFunction: {func['name']}", output_file)
        write_to_output(f"Summary: {func['summary']}", output_file)
    
    # Verify content relationships
    file_summary = hierarchy["file_summary"]
    class_summaries = hierarchy["classes"]
    
    assert any(cls["name"] == "RiskCalculator" for cls in class_summaries), \
        "Should include RiskCalculator class"
    assert any(cls["name"] == "RiskFactor" for cls in class_summaries), \
        "Should include RiskFactor class"
    write_to_output("\nHierarchical summary structure verification passed", output_file)

if __name__ == "__main__":
    # Create output file
    with open("summarization_test_output.txt", "w") as output_file:
        write_to_output("=== Starting Summarization Tests ===\n", output_file)
        test_file_level_summary(output_file)
        test_chunk_level_summary(output_file)
        test_hierarchical_summary(output_file)
        write_to_output("\n=== Summarization Tests Completed ===", output_file) 