#!/usr/bin/env python3
"""
Model Documentation Agent - Direct Implementation
This is a direct implementation of a ReAct-style agent using Claude without LangChain's agent framework.
"""
import os
import sys
from typing import List, Dict, Any, Optional, Union, Tuple
import json
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the root directory to the path
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Import needed modules from project
from src.utils.config import Config
from src.debug.logger import ModelDocDebugger
from langchain_anthropic import ChatAnthropic
from langchain.tools import BaseTool, tool

# Define simple test tools since we're having issues with the core_tools
@tool
def describe_codebase(query: str) -> str:
    """
    Describe the structure and key components of the codebase.
    Input: A query about what aspect of the codebase you want to know about.
    Output: A description of the requested aspect of the codebase.
    """
    return """
    This Model Documentation Agent codebase consists of several key components:
    
    1. Agent Implementation:
        - Custom Claude agent that avoids the 'functions' parameter issue
        - Direct implementation without using LangChain's agent framework
        - Supports both mock mode and real API calls
    
    2. Tools:
        - Code summarization tools (summarize files, generate hierarchical summaries)
        - Documentation generation tools (create outlines, draft sections)
        
    3. Utils:
        - LLM factory for creating LLM instances
        - Config management
        - Debugging and logging utilities
        
    4. Data Handling:
        - Code loading and parsing
        - Template management
        
    The codebase supports both mock mode (for testing without API calls) and real API mode.
    """

@tool
def mock_vs_real_api(detail_level: str = "high") -> str:
    """
    Explain the difference between mock LLM and real API calls in this codebase.
    Input: detail_level can be "low", "medium", or "high"
    Output: An explanation of the differences between mock and real mode
    """
    return """
    In this codebase, there are two primary modes of operation: mock mode and real API mode.
    
    MOCK MODE:
    - Uses FakeListLLM from langchain.llms.fake
    - No actual API calls are made to Anthropic/Claude
    - Predefined responses are returned based on pattern matching
    - Used for testing, development, and when no API key is available
    - Configured via config.llm.mock_mode = True or by passing mock_mode=True
    - Found in src/utils/llm_factory.py where it creates a FakeListLLM instance
    - Allows offline development and testing without using API credits
    
    REAL API MODE:
    - Makes actual calls to the Anthropic Claude API
    - Requires a valid ANTHROPIC_API_KEY in environment variables
    - Creates a ChatAnthropic instance that communicates with the real API
    - Provides genuine AI responses but costs API credits
    - Used in production environments and for final testing
    - More computationally intensive and takes longer to process
    - Implementation handles proper formatting of requests and responses
    
    IMPLEMENTATION DETAILS:
    - In src/utils/llm_factory.py, the create_llm function decides whether to return a 
      FakeListLLM or a real ChatAnthropic instance based on the mock_mode parameter
    - When using the custom Claude agent, special handling is needed to avoid the 
      'functions' parameter issue that occurs with real API calls
    
    The main difference is that mock mode uses predefined responses for rapid development
    and testing, while real API mode provides actual Claude-generated responses but
    requires an API key and uses API credits.
    """

@tool
def explain_functions_issue(query: str = "detailed") -> str:
    """
    Explain the 'functions' parameter issue with Claude and LangChain agents.
    Input: The level of detail desired ("brief", "detailed", or any specific question)
    Output: An explanation of the issue and our custom solution
    """
    return """
    THE "FUNCTIONS" PARAMETER ISSUE WITH CLAUDE AND LANGCHAIN
    
    The exact error we encountered was: "Messages.create() got an unexpected keyword argument 'functions'"
    
    ISSUE DETAILS:
    - LangChain's standard agent implementations use a parameter called "functions" when making API calls
    - This parameter works with OpenAI's API but is COMPLETELY UNSUPPORTED by Anthropic's Claude API
    - Anthropic's Claude API does not have ANY parameter called "functions"
    - When LangChain tries to use Claude with these agent implementations, it incorrectly passes the "functions" parameter
    - This results in the error: "Messages.create() got an unexpected keyword argument 'functions'"
    
    NOTE: The issue is NOT about format conversion between different styles of function parameters.
    Claude simply does not accept a "functions" parameter at all in its API.
    
    OUR SOLUTION (Direct Implementation):
    - We built a completely custom implementation that directly uses the Claude API
    - Our implementation:
      * Uses a ReAct-style prompt to structure the agent's reasoning
      * Directly parses Claude's responses for actions and action inputs
      * Handles tool execution and conversation management
      * Avoids any dependency on LangChain's agent framework
      * Never attempts to pass a "functions" parameter to Claude's API
    - This approach gives us full control over the interaction pattern and avoids the "functions" parameter issue
    
    IMPLEMENTATION DETAILS:
    In our ModelDocAgent class (this file you're currently running), we:
    1. Initialize Claude directly through LangChain's ChatAnthropic but NEVER try to use LangChain's agent framework
    2. Use a custom ReAct prompt template that includes tool descriptions inline in the prompt text
    3. Handle the conversation flow and state management ourselves using a simple list of messages
    4. Parse Claude's text responses to extract actions and inputs using string parsing
    5. Execute tools using direct invocation rather than through agent frameworks
    6. Format observations from tools as messages in the conversation history
    
    This approach completely bypasses the "functions" parameter issue by never attempting to use that parameter with Claude's API.
    """

# List of custom tools
TOOLS = [
    describe_codebase,
    mock_vs_real_api,
    explain_functions_issue
]

# ReAct prompt template for model documentation agent
MODEL_DOC_AGENT_TEMPLATE = """You are a specialized assistant for documenting risk models and applications.
Your primary goal is to help users understand and document complex codebases by leveraging provided tools.

You have access to the following tools:
{tool_descriptions}

To use a tool, output a response in the following format:
```
Thought: I need to analyze what the user is asking for
Action: tool_name
Action Input: {{"param1": value1, "param2": value2}}
```

The Action Input should be a valid JSON object with the parameters required by the tool.

After receiving the tool's response, continue your reasoning:
```
Observation: [Tool output will appear here]
Thought: Now I see that...
```

Once you're ready to give a final answer, use:
```
Thought: I now have all the information needed
Final Answer: [Your detailed and well-structured answer here]
```

Key capabilities you have:
- Analyze and describe codebase structure
- Explain differences between mock and real API usage
- Provide technical details about the implementation

Begin by understanding the user's request and using the appropriate tools step-by-step.

User request: {question}
"""

class ModelDocAgent:
    """
    A direct implementation of the Model Documentation Agent using Claude.
    """
    
    def __init__(
        self,
        tools: List[BaseTool],
        model_name: str = "claude-3-opus-20240229",
        temperature: float = 0.2,
        max_tokens: int = 4096,
        verbose: bool = True,
        debugger: Optional[ModelDocDebugger] = None
    ):
        # Store configuration
        self.tools = tools
        self.tool_map = {tool.name: tool for tool in tools}
        self.verbose = verbose
        self.config = Config()
        self.debugger = debugger or ModelDocDebugger(logger_name="ModelDocAgent", debug_level="INFO")
        
        # Initialize Claude model
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
            
        self.llm = ChatAnthropic(
            model=model_name,
            temperature=temperature,
            max_tokens_to_sample=max_tokens,
            anthropic_api_key=api_key
        )
        
        self.debugger.logger.info(f"Initialized ModelDocAgent with model: {model_name}")
        
    def _parse_reaction(self, text: str) -> Dict[str, Any]:
        """Parse the agent's reaction text to extract action, action input, or final answer."""
        if "Final Answer:" in text:
            final_answer = text.split("Final Answer:")[-1].strip()
            return {"type": "final_answer", "content": final_answer}
            
        if "Action:" in text and "Action Input:" in text:
            action_text = text.split("Action:")[-1].split("\n")[0].strip()
            action_input_text = text.split("Action Input:")[-1].split("\n")[0].strip()
            
            try:
                # Try to parse action input as JSON
                if action_input_text.startswith("{") and action_input_text.endswith("}"):
                    action_input = json.loads(action_input_text)
                else:
                    # If not valid JSON, use as string
                    action_input = action_input_text
                    
                return {
                    "type": "action",
                    "action": action_text,
                    "action_input": action_input
                }
            except json.JSONDecodeError as e:
                self.debugger.log_exception("parse_reaction", e, {"action_input_text": action_input_text})
                # Fall back to using the raw string
                return {
                    "type": "action",
                    "action": action_text,
                    "action_input": action_input_text
                }
                
        # Default fallback - treat as final answer if we can't parse
        return {"type": "final_answer", "content": text}
    
    def _execute_tool(self, tool_name: str, tool_input: Any) -> str:
        """Execute a tool and return its result as a string."""
        if tool_name not in self.tool_map:
            error_msg = f"Error: Tool '{tool_name}' not found."
            self.debugger.logger.warning(error_msg)
            return error_msg
            
        tool = self.tool_map[tool_name]
        
        try:
            self.debugger.start_timer(f"tool_{tool_name}")
            
            # Handle different tool input types
            if isinstance(tool_input, dict):
                # Special handling for invoke/run instead of call
                if hasattr(tool, "invoke"):
                    result = tool.invoke(tool_input)
                else:
                    # If no invoke method, try with first parameter
                    if len(tool_input) == 1:
                        param_name = list(tool_input.keys())[0]
                        result = tool.run(tool_input[param_name])
                    else:
                        # Error handling
                        self.debugger.logger.warning(f"Tool {tool_name} doesn't support multiple parameters with invoke")
                        result = "Error: Tool doesn't support multiple parameters in this implementation."
            elif isinstance(tool_input, str):
                # Use the run method which is usually simpler
                result = tool.run(tool_input)
            else:
                # Direct pass-through
                result = tool.run(tool_input)
             
            elapsed = self.debugger.end_timer(f"tool_{tool_name}")
            self.debugger.logger.info(f"Tool '{tool_name}' executed in {elapsed:.2f} seconds")
                
            # Convert result to string representation
            if isinstance(result, dict):
                # For dictionary results, format nicely
                result_str = json.dumps(result, indent=2)
            else:
                result_str = str(result)
                
            # If result is very long (over 50K chars), truncate it
            if len(result_str) > 50000:
                result_str = result_str[:25000] + "\n...[truncated]...\n" + result_str[-25000:]
                self.debugger.logger.warning(f"Tool output truncated for '{tool_name}' (over 50K chars)")
                
            return result_str
        except Exception as e:
            self.debugger.log_exception("execute_tool", e, {"tool_name": tool_name, "tool_input": tool_input})
            return f"Error executing tool '{tool_name}': {str(e)}"
    
    def run(self, query: str, max_iterations: int = 15) -> str:
        """Run the agent to answer a documentation request."""
        self.debugger.logger.info(f"Running ModelDocAgent on query: {query}")
        self.debugger.start_timer("query_execution")
        
        if self.verbose:
            print(f"\n---- Starting ModelDocAgent on query: '{query}' ----")
            
        # Prepare the initial prompt
        tool_descriptions = "\n".join([f"- {tool.name}: {tool.description}" for tool in self.tools])
        prompt = MODEL_DOC_AGENT_TEMPLATE.format(
            question=query,
            tool_descriptions=tool_descriptions
        )
        
        # Initialize the conversation with the prompt
        messages = [{"role": "user", "content": prompt}]
        
        for i in range(max_iterations):
            if self.verbose:
                print(f"\n---- Iteration {i+1}/{max_iterations} ----")
                
            # Get response from Claude
            self.debugger.start_timer(f"iteration_{i+1}")
            response = self.llm.invoke(messages)
            response_text = response.content
            self.debugger.end_timer(f"iteration_{i+1}")
            
            if self.verbose:
                print(f"\nAgent: {response_text}")
                
            # Parse the response
            reaction = self._parse_reaction(response_text)
            
            # If it's a final answer, return it
            if reaction["type"] == "final_answer":
                elapsed = self.debugger.end_timer("query_execution")
                self.debugger.logger.info(f"Query completed in {elapsed:.2f} seconds after {i+1} iterations")
                return reaction["content"]
                
            # Otherwise, execute the tool
            tool_name = reaction["action"]
            tool_input = reaction["action_input"]
            
            if self.verbose:
                print(f"\nExecuting tool: {tool_name}")
                print(f"Tool input: {tool_input}")
                
            # Execute the tool
            observation = self._execute_tool(tool_name, tool_input)
            
            if self.verbose:
                if len(observation) > 1000:
                    print(f"Tool output: {observation[:500]}...[truncated]...{observation[-500:]}")
                else:
                    print(f"Tool output: {observation}")
                
            # Add the response and observation to the conversation
            messages.append({"role": "assistant", "content": response_text})
            messages.append({"role": "user", "content": f"Observation: {observation}"})
            
        # If we hit the iteration limit
        elapsed = self.debugger.end_timer("query_execution")
        self.debugger.logger.warning(f"Query reached maximum iterations ({max_iterations}) after {elapsed:.2f} seconds")
        return "Maximum iterations reached. Here's what I found so far:\n\n" + response_text

if __name__ == "__main__":
    print("-" * 80)
    print("MODEL DOCUMENTATION AGENT - DIRECT IMPLEMENTATION")
    print("-" * 80)

    try:
        # Initialize debugger
        debugger = ModelDocDebugger(logger_name="ModelDocTest", debug_level="INFO", log_to_console=True)
        
        # Create the agent with our custom tools
        agent = ModelDocAgent(tools=TOOLS, verbose=True, debugger=debugger)
        print("\nAgent initialized successfully!\n")
        
        # Example queries to test
        queries = [
            "What is the structure of this codebase?",
            "What is the difference between using a mock LLM and a real API call in this codebase?",
            "Can you explain in detail how mock mode works compared to real API mode?",
            "Explain the 'functions' parameter issue with Claude and LangChain agents."
        ]
        
        # Run the example query
        idx = 3  # Choose which query to run
        query = queries[idx]
        print(f"\nTesting with query: '{query}'")
        
        # Run the agent
        result = agent.run(query)
        
        print(f"\nFinal Answer: {result}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()
        
    print("\n" + "-" * 80)
    print("TEST COMPLETE")
    print("-" * 80) 