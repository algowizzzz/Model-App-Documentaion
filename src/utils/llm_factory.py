"""
Factory utility for creating LLM instances.
"""

import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain.chat_models.base import BaseChatModel
from langchain.schema import HumanMessage

# Load environment variables from .env file
load_dotenv()

@dataclass
class LLMConfig:
    """Configuration for LLM instances."""
    model_name: str = "claude-3-haiku-20240307"
    temperature: float = 0.2
    max_tokens: int = 1000
    top_p: float = 0.8
    api_key: Optional[str] = None

def create_llm(model_name: Optional[str] = None, temperature: float = 0.2, api_key: Optional[str] = None, **kwargs) -> BaseChatModel:
    """Create a new LLM instance with the specified configuration."""
    config = LLMConfig(temperature=temperature, api_key=api_key)
    
    # Use provided model_name if passed as parameter
    if model_name:
        config.model_name = model_name
    
    api_key = config.api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "Anthropic API key not found. Please set ANTHROPIC_API_KEY environment variable "
            "or provide it via api_key parameter."
        )
    
    return ChatAnthropic(
        model=config.model_name,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        top_p=config.top_p,
        anthropic_api_key=api_key
    )

def generate_text(prompt: str) -> str:
    """Generate text from a prompt using the LLM.
    
    Args:
        prompt: The prompt to send to the LLM
        
    Returns:
        The generated text response
    """
    llm = create_llm()
    messages = [HumanMessage(content=prompt)]
    response = llm.invoke(messages)
    return response.content 