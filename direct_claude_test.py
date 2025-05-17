#!/usr/bin/env python3
"""
Direct Claude API test without using LangChain's agents.
This approach uses a simpler ReAct pattern directly implemented.
"""
import os
import sys
from typing import List, Dict, Any, Optional, Union, Tuple
import json
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import only what we need
from langchain_anthropic import ChatAnthropic
from langchain.tools import BaseTool, tool
from langchain.prompts import PromptTemplate

# Simple tools for testing
@tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers together."""
    return a * b

@tool
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b

# Tools list
tools = [multiply, add]

# ReAct prompt template
REACT_TEMPLATE = """You are a specialized assistant that uses tools to solve problems.

You have access to the following tools:
{tool_descriptions}

To use a tool, output a response in the following format:
```
Thought: I need to solve this step-by-step
Action: tool_name
Action Input: {{"param1": value1, "param2": value2}}
```

The Action Input should be a valid JSON object with the parameters required by the tool.

After receiving the tool's response, continue your reasoning:
```
Observation: [Tool output will appear here]
Thought: Now I can see...
```

Once you're ready to give a final answer, use:
```
Thought: I now know the answer
Final Answer: [Your answer here]
```

Begin solving the user's question step-by-step.

User question: {question}
"""

class DirectClaudeAgent:
    """
    A direct implementation of a ReAct-style agent using Claude without LangChain's agent framework.
    """
    
    def __init__(
        self,
        tools: List[BaseTool],
        model_name: str = "claude-3-opus-20240229",
        temperature: float = 0.2,
        max_tokens: int = 4096,
        verbose: bool = True
    ):
        # Store configuration
        self.tools = tools
        self.tool_map = {tool.name: tool for tool in tools}
        self.verbose = verbose
        
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
        
        # Prepare tool descriptions
        tool_descriptions = "\n".join([f"- {tool.name}: {tool.description}" for tool in tools])
        
        # Create prompt template
        self.prompt_template = PromptTemplate(
            template=REACT_TEMPLATE,
            input_variables=["question", "tool_descriptions"]
        )
        
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
            except json.JSONDecodeError:
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
            return f"Error: Tool '{tool_name}' not found."
            
        tool = self.tool_map[tool_name]
        
        try:
            # Handle different tool input types
            if isinstance(tool_input, dict):
                result = tool(**tool_input)
            elif isinstance(tool_input, str):
                try:
                    # Try to parse as JSON if string
                    input_dict = json.loads(tool_input)
                    result = tool(**input_dict)
                except json.JSONDecodeError:
                    # Use as single argument if not JSON
                    result = tool(tool_input)
            else:
                # Direct pass-through
                result = tool(tool_input)
                
            return str(result)
        except Exception as e:
            return f"Error executing tool '{tool_name}': {str(e)}"
    
    def run(self, query: str, max_iterations: int = 10) -> str:
        """Run the agent to solve a query."""
        if self.verbose:
            print(f"\n---- Starting DirectClaudeAgent on query: '{query}' ----")
            
        # Prepare the initial prompt
        prompt = self.prompt_template.format(
            question=query,
            tool_descriptions="\n".join([f"- {tool.name}: {tool.description}" for tool in self.tools])
        )
        
        # Initialize the conversation with the prompt
        messages = [{"role": "user", "content": prompt}]
        
        for i in range(max_iterations):
            if self.verbose:
                print(f"\n---- Iteration {i+1} ----")
                
            # Get response from Claude
            response = self.llm.invoke(messages)
            response_text = response.content
            
            if self.verbose:
                print(f"\nClaude: {response_text}")
                
            # Parse the response
            reaction = self._parse_reaction(response_text)
            
            # If it's a final answer, return it
            if reaction["type"] == "final_answer":
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
                print(f"Tool output: {observation}")
                
            # Add the response and observation to the conversation
            messages.append({"role": "assistant", "content": response_text})
            messages.append({"role": "user", "content": f"Observation: {observation}"})
            
        # If we hit the iteration limit, return the last response
        return "Maximum iterations reached. Could not find a final answer."

if __name__ == "__main__":
    print("-" * 80)
    print("DIRECT CLAUDE AGENT TEST")
    print("-" * 80)

    try:
        # Create the agent
        agent = DirectClaudeAgent(tools=tools, verbose=True)
        print("\nAgent initialized successfully!\n")
        
        # Test with a query that requires tools
        query = "What is 15 multiplied by 7, and then that result added to 32?"
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