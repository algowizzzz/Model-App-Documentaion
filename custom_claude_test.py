#!/usr/bin/env python3
"""
Test script for custom Claude agent implementation.
This demonstrates using a custom ReAct-style agent that avoids the 'functions' parameter issue.
"""
import os
import sys
from dotenv import load_dotenv
import traceback

# Load environment variables
load_dotenv()

# Add the src directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import our custom Claude agent
from src.utils.claude_agent import create_claude_agent
from src.tools.core_tools import TOOLS
from src.debug.logger import ModelDocDebugger

print("-" * 80)
print("CUSTOM CLAUDE AGENT TEST")
print("-" * 80)

# Check for the API key
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    print("Error: ANTHROPIC_API_KEY environment variable is not set.")
    sys.exit(1)

print(f"API key found: {api_key[:10]}...")

# Initialize a debugger
debugger = ModelDocDebugger(logger_name="CustomClaudeTest", debug_level="INFO")

try:
    print("\nInitializing custom Claude agent...")
    agent = create_claude_agent(
        tools=TOOLS,
        model_name="claude-3-opus-20240229",
        temperature=0.2,
        verbose=True
    )
    
    print("\nAgent initialized successfully!")
    
    # Test a simple query first
    print("\nTesting with a simple query...")
    response = agent.invoke({
        "input": "What types of tools do you have available?"
    })
    print(f"\nResponse: {response.get('output', 'No output')}")
    
    # Test with a tool usage query
    print("\nTesting with a tool usage query...")
    response = agent.invoke({
        "input": "Can you summarize the code files in the 'codebase' directory?"
    })
    print(f"\nResponse: {response.get('output', 'No output')}")
    
except Exception as e:
    print(f"Error: {str(e)}")
    traceback.print_exc()

print("\n" + "-" * 80)
print("TEST COMPLETE")
print("-" * 80) 