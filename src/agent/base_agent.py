from langchain.agents import initialize_agent, AgentExecutor
from langchain.agents.agent_types import AgentType
# ChatAnthropic is not directly instantiated, create_llm handles it
# from langchain_anthropic import ChatAnthropic
import os
import sys

# Add path context for absolute imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, ".."))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Use absolute imports
from src.tools.core_tools import TOOLS
from src.utils.llm_factory import create_llm
from src.utils.config import Config
from src.debug.logger import ModelDocDebugger
from src.utils.claude_agent import create_claude_agent  # Import our custom Claude agent

def create_documentation_agent(config: Config, debugger: ModelDocDebugger, use_mock: bool = False) -> AgentExecutor:
    """
    Initializes and returns the Model Documentation Agent.

    Args:
        config (Config): Configuration object.
        debugger (ModelDocDebugger): Debugger instance for logging.
        use_mock (bool): Whether to use mock LLM for testing.

    Returns:
        AgentExecutor: The initialized LangChain agent executor.
    """
    debugger.logger.info("Initializing Model Documentation Agent...")

    # Check for API key in environment
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        debugger.logger.info("Found API key in environment variables")
        print(f"API key is available and starts with: {api_key[:10]}...")
    else:
        debugger.logger.warning("No API key found in environment variables")
        print("API key is not available in environment")
        
    # use_mock will override even if API key is available
    if use_mock:
        debugger.logger.info("Using mock mode as explicitly requested")
        print("Explicit mock mode requested")
        
        # Create a mock LLM and use the standard agent
        llm = create_llm(
            model_name=config.get("llm.model_name", "claude-3-opus-20240229"),
            temperature=config.get("llm.temperature", 0.2),
            api_key=api_key,
            debugger=debugger,
            mock_mode=True  # Force mock mode
        )

        system_message_content = config.get("agent.system_message", """
You are a specialized assistant for documenting risk models and applications.
Your primary goal is to help users understand and document complex codebases
by leveraging provided tools to analyze code, work with documentation templates,
and generate various documentation artifacts.

Key Capabilities:
- Summarize individual code files or entire codebases.
- Generate hierarchical summaries to provide a high-level overview.
- Create documentation outlines based on JSON templates.
- Draft specific sections of documentation using code insights and templates.
- Offer suggestions to improve existing documentation drafts.

Interaction Style:
- Maintain a professional, clear, and concise tone.
- When asked to perform a task, clearly state the tool you are using and the key inputs.
- If you encounter an error or cannot fulfill a request, explain the issue clearly.
- You can be asked to dynamically adjust your approach if needed.
""")
    
        # Using a simpler agent type for mock mode
        agent_kwargs = {
            "prefix": system_message_content,
        }

        try:
            documentation_agent = initialize_agent(
                tools=TOOLS,
                llm=llm,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=config.get("agent.verbose", True),
                handle_parsing_errors=True,
                agent_kwargs=agent_kwargs,
                max_iterations=config.get("agent.max_iterations", 15)
            )
            debugger.logger.info("Model Documentation Agent initialized successfully (mock mode).")
            return documentation_agent
        except Exception as e:
            debugger.log_exception("create_documentation_agent", e, {"agent_type": "ZERO_SHOT_REACT_DESCRIPTION", "mode": "mock"})
            raise RuntimeError(f"Failed to initialize the documentation agent in mock mode: {str(e)}")
    
    else:
        # Use the custom Claude agent implementation for real API usage
        try:
            documentation_agent = create_claude_agent(
                tools=TOOLS,
                model_name=config.get("llm.model_name", "claude-3-opus-20240229"),
                temperature=config.get("llm.temperature", 0.2),
                max_tokens=config.get("llm.max_tokens", 4096),
                verbose=config.get("agent.verbose", True)
            )
            debugger.logger.info("Model Documentation Agent initialized successfully (real Claude API).")
            return documentation_agent
        except Exception as e:
            debugger.log_exception("create_documentation_agent", e, {"mode": "custom_claude_agent"})
            raise RuntimeError(f"Failed to initialize custom Claude agent: {str(e)}")

if __name__ == '__main__':
    # This is a simple test script that can be run to check agent initialization
    # In a real application, Config and ModelDocDebugger would be set up more centrally.
    
    print("Testing agent initialization...")
    test_config = Config() # Uses default config.py
    test_debugger = ModelDocDebugger(logger_name="AgentTest", debug_level="DEBUG", log_to_console=True)
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY not set in environment. LLM calls will fail.")
        # You might want to exit or use a mock LLM for offline testing.
    
    try:
        agent_executor = create_documentation_agent(config=test_config, debugger=test_debugger)
        print(f"Agent initialized: {agent_executor}")
        
        # A simple test invocation (requires a correctly set up environment and API key)
        # response = agent_executor.invoke({"input": "Hello, who are you?"})
        # print(f"Agent response: {response}")

    except RuntimeError as e:
        print(f"Error during agent test: {e}")
    except ImportError:
        print("ImportError occurred. Make sure all dependencies are installed and paths are correct.")
        print("You might need to run 'pip install -r requirements.txt' from the 'model-doc-agent' directory.")
        print("And ensure PYTHONPATH is set up if running from outside the project root.") 