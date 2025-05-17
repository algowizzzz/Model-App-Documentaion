#!/usr/bin/env python3
"""
Sample run for the Refactored Model Documentation Agent
Demonstrates key functionalities of the agent.
"""
import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Adjust path to import from parent directory (src)
# This is essential for making both relative imports work when running directly
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, "..")) # Go up one level to src/
project_root = os.path.abspath(os.path.join(src_dir, "..")) # Go up another level to model-doc-agent/

# Add the src directory to the Python path
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now use absolute imports from the src package
from src.agent.base_agent import create_documentation_agent
from src.utils.config import Config
from src.debug.logger import ModelDocDebugger

def main():
    """Main function to run the sample agent interactions."""
    print("Initializing Model Documentation Agent for sample run...")
    
    # Initialize Config and Debugger
    config = Config() 
    
    # For the sample run, check if the API key is available
    api_key = os.getenv("ANTHROPIC_API_KEY")
    use_mock = False
    
    if not api_key:
        print("ANTHROPIC_API_KEY not found in environment variables.")
        print("Running in mock mode for testing purposes.")
        use_mock = True
    else:
        print(f"Found ANTHROPIC_API_KEY in environment. Using real API mode.")
        print(f"API Key starts with: {api_key[:10]}...")

    # Initialize debugger with correct parameters
    debugger = ModelDocDebugger(logger_name="SampleRun", debug_level="INFO")
    # Configure console output handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    debugger.logger.addHandler(console_handler)
    
    try:
        agent_executor = create_documentation_agent(config=config, debugger=debugger, use_mock=use_mock)
        print("Agent initialized successfully.")
    except RuntimeError as e:
        debugger.logger.error(f"Failed to initialize agent: {e}")
        return
    except ImportError as e:
        debugger.logger.error(f"ImportError during agent initialization: {e}. Make sure paths and dependencies are correct.")
        return

    # Define paths relative to the project root (model-doc-agent/)
    codebase_dir = "codebase/" # Relative to model-doc-agent/
    template_file = "templates/model_doc_template.json" # Relative to model-doc-agent/

    # --- Example Agent Interactions ---
    # Note: The CONVERSATIONAL_REACT_DESCRIPTION agent has memory. 
    # It will try to use information from previous steps if relevant.

    prompts = [
        # 1. Summarize files in the codebase directory
        f"Please summarize all code files in the '{codebase_dir}' directory. I need individual summaries for each file.",
        
        # 2. Generate a hierarchical summary based on the previous file summaries
        "Now, based on the file summaries you just created, can you generate a single hierarchical summary of the entire codebase?",
        
        # 3. Generate an outline from the specified documentation template
        f"Next, please generate a documentation outline using the template file located at '{template_file}'.",
        
        # 4. Draft a specific section (e.g., Methodology) from the template.
        #    The agent needs to identify the section ID (e.g., "methodology") from the template, 
        #    and gather relevant context (summaries, snippets) for that section.
        #    The prompt guides the agent to use its available tools and information.
        f"I need to draft a documentation section. Using the template from '{template_file}', find the section with ID 'methodology'. Then, gather relevant code summaries and other contextual information you have to draft the content for this 'methodology' section.",

        # 5. Suggest improvements on a hypothetical combined document.
        #    This prompt is a bit more complex as it implies a document exists. 
        #    For a real test, one might first concatenate outputs from previous steps.
        #    Here, we ask it to imagine it has a draft and to use its code understanding.
        "Imagine I have a preliminary draft of the model documentation. Based on your understanding of the codebase (from the summaries), could you suggest 3-5 key areas where the documentation could be improved or expanded? Focus on technical accuracy and completeness."
    ]

    for i, prompt_text in enumerate(prompts):
        print(f"\n--- Running Prompt {i+1} ---")
        print(f"User: {prompt_text}")
        try:
            response = agent_executor.invoke({"input": prompt_text})
            print(f"Agent: {response.get('output', 'No output found.')}")
            # If there are intermediate steps and you want to see them:
            # if "intermediate_steps" in response and response["intermediate_steps"]:
            #     print("Intermediate Steps:")
            #     for step in response["intermediate_steps"]:
            #         print(f"  - Tool: {step[0].tool}, Input: {step[0].tool_input}, Log: {step[0].log.strip()}")
            #         print(f"    Output: {step[1]}")

        except Exception as e:
            debugger.logger.error(f"Error during agent interaction for prompt {i+1}: {e}")
            print(f"Agent Error: Could not complete the request due to: {str(e)}")

    print("\n--- Sample run finished ---")

if __name__ == "__main__":
    main() 