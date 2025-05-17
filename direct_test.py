#!/usr/bin/env python3
"""
Demonstration of the Model Documentation Agent in mock mode.
This is because we found a compatibility issue with Claude and LangChain agents.
"""
import os
import sys

# Import necessary components
from src.agent.base_agent import create_documentation_agent
from src.utils.config import Config
from src.debug.logger import ModelDocDebugger

print("-"*80)
print("MODEL DOCUMENTATION AGENT - MOCK DEMONSTRATION")
print("-"*80)
print("\nNOTE: We've set this to mock mode because we identified an issue with LangChain's")
print("      agent implementation and Claude's API. The 'functions' parameter is being")
print("      incorrectly passed to Claude, which requires different parameters than OpenAI models.")
print("\nTo fix this in a production environment, you would need to:")
print("1. Use a custom agent implementation that avoids sending the 'functions' parameter to Claude")
print("2. Create a ReAct-style prompt format for Claude that uses a different structure")
print("3. Or implement a custom agent using LangGraph as recommended in the LangChain warnings")
print("\nWe have verified that:")
print("1. Direct Claude API calls work correctly with your API key")
print("2. The issue is specifically with how LangChain integrates with the Claude API")
print("3. The model documentation agent functionality can work with a custom implementation")
print("-"*80)

# Initialize Config
config = Config() 

# Initialize debugger  
debugger = ModelDocDebugger(logger_name="DirectTest", debug_level="INFO")

try:
    # Force mock mode to demonstrate functionality
    use_mock = True
    print(f"Running in {'MOCK' if use_mock else 'real API'} mode for demonstration")
    
    # Create agent with mock mode enabled
    agent = create_documentation_agent(config=config, debugger=debugger, use_mock=use_mock)
    print("Agent initialized successfully\n")
    
    # Define paths relative to the project root
    codebase_dir = "codebase/" 
    template_file = "templates/model_doc_template.json"
    
    # Define the sequence of prompts that show the workflow
    prompts = [
        # 1. Summarize files in the codebase directory
        f"Please summarize all code files in the '{codebase_dir}' directory. I need individual summaries for each file.",
        
        # 2. Generate a hierarchical summary
        "Now, based on the file summaries you just created, can you generate a single hierarchical summary of the entire codebase?",
        
        # 3. Generate a documentation outline from the template
        f"Next, please generate a documentation outline using the template file located at '{template_file}'.",
        
        # 4. Draft a specific section (Methodology)
        f"I need to draft a documentation section. Using the template from '{template_file}', find the section with ID 'methodology'. Then, gather relevant code summaries and other contextual information to draft the content for this 'methodology' section.",

        # 5. Suggest improvements
        "Imagine I have a preliminary draft of the model documentation. Based on your understanding of the codebase, could you suggest 3-5 key areas where the documentation could be improved or expanded? Focus on technical accuracy and completeness."
    ]
    
    # Run through each prompt to demonstrate the workflow
    for i, prompt in enumerate(prompts):
        print(f"\n{'='*50}")
        print(f"STEP {i+1}: {prompt.split('.')[0] if '.' in prompt else prompt[:50]}...")
        print(f"{'='*50}")
        print(f"User: {prompt}")
        
        response = agent.invoke({"input": prompt})
        print(f"\nAgent: {response.get('output', 'No output')}")
        
    print("\n" + "-"*80)
    print("MOCK DEMONSTRATION COMPLETE")
    print("\nIMPORTANT: In a production version, you would implement a custom agent that")
    print("           properly interfaces with Claude's API or switch to LangGraph.")
    print("-"*80)
    
except Exception as e:
    print(f"Error: {str(e)}") 