"""
Custom Claude-compatible agent implementation to solve the 'functions' parameter issue.
"""
from typing import List, Dict, Any, Optional, Union, Tuple, cast, ClassVar
import os
from langchain_anthropic import ChatAnthropic
from langchain.tools import BaseTool
from langchain.agents import AgentExecutor, initialize_agent, AgentType
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.callbacks.manager import CallbackManagerForChainRun, AsyncCallbackManagerForChainRun
from langchain.schema.agent import AgentAction, AgentFinish
from langchain.agents.agent import Agent, AgentOutputParser, LLMSingleActionAgent
from langchain_core.runnables import Runnable
from langchain.schema.runnable import RunnableMap, RunnableConfig
from pydantic import BaseModel, Field

# Define the ReAct style prompt template for Claude
REACT_TEMPLATE = """You are a specialized assistant for documenting risk models and applications.
Your primary goal is to help users understand and document complex codebases by leveraging provided tools.

To solve this task, you have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Question: {input}
{agent_scratchpad}"""

class ClaudeReActOutputParser(AgentOutputParser):
    """Output parser for the ReAct format."""
    
    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        """Parse text into an agent action or finish."""
        if "Final Answer:" in text:
            return AgentFinish(
                return_values={"output": text.split("Final Answer:")[-1].strip()},
                log=text
            )
        
        # Look for Action/Action Input pattern
        try:
            action_match = text.split("Action:")[-1].split("\n")[0].strip()
            action_input_match = text.split("Action Input:")[-1].split("\n")[0].strip()
            
            # If we found both, return an AgentAction
            return AgentAction(
                tool=action_match,
                tool_input=action_input_match,
                log=text
            )
        except Exception:
            # If parsing fails, return the finish with original text
            return AgentFinish(
                return_values={"output": text},
                log=text
            )

def create_claude_agent(
    tools: List[BaseTool],
    model_name: str = "claude-3-opus-20240229",
    temperature: float = 0.2,
    max_tokens: int = 4096,
    verbose: bool = True
) -> AgentExecutor:
    """
    Create a Claude-compatible agent that avoids the 'functions' parameter issue.
    
    This uses a simpler approach with initialize_agent and a specific agent type.
    """
    # Get API key from environment
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is required")
    
    # Initialize the Claude model
    llm = ChatAnthropic(
        model=model_name,
        temperature=temperature,
        max_tokens_to_sample=max_tokens,
        anthropic_api_key=api_key
    )
    
    # Format tools for the prompt
    tool_descriptions = "\n".join([f"{tool.name}: {tool.description}" for tool in tools])
    tool_names = ", ".join([tool.name for tool in tools])
    
    # Create prompt template
    prompt = PromptTemplate(
        template=REACT_TEMPLATE,
        input_variables=["input", "agent_scratchpad"],
        partial_variables={"tools": tool_descriptions, "tool_names": tool_names}
    )
    
    # Create the LLM chain
    llm_chain = LLMChain(
        llm=llm,
        prompt=prompt
    )
    
    # Create the output parser
    output_parser = ClaudeReActOutputParser()
    
    # Create the agent with LLMSingleActionAgent
    agent = LLMSingleActionAgent(
        llm_chain=llm_chain,
        output_parser=output_parser,
        stop=["\nObservation:"],
        allowed_tools=[tool.name for tool in tools],
    )
    
    # Create and return the agent executor
    return AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        verbose=verbose,
        max_iterations=15,
        handle_parsing_errors=True
    ) 