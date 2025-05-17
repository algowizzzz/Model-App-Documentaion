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

    # Get LLM settings from config, with defaults
    # create_llm should internally use config for model_name, temperature etc.
    # We pass the debugger instance to create_llm if it's designed to use it.
    llm = create_llm(
        model_name=config.get("llm.model_name", "claude-3-opus-20240229"),
        temperature=config.get("llm.temperature", 0.2),
        # max_tokens=config.get("llm.max_tokens", 1000), # Example if create_llm supports it
        api_key=config.get("anthropic_api_key"), # create_llm should handle API key logic
        debugger=debugger,
        mock_mode=use_mock or config.get("mock_mode", False)
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
    
    # Using a more suitable agent type for Claude and custom tools
    # CONVERSATIONAL_REACT_DESCRIPTION is a good choice for tools with descriptions.
    # For this agent type, the system message is often passed as part of the prompt to the agent,
    # or handled by the LLM itself if it's a ChatModel.
    # initialize_agent might handle this differently depending on type.
    # For Chat models, a system message in the HumanMessagePromptTemplate or similar is common.
    # Let's try passing it via agent_kwargs if using CONVERSATIONAL_REACT_DESCRIPTION.
    
    agent_kwargs = {
        "system_message": system_message_content,
        # "extra_prompt_messages": [SystemMessagePromptTemplate.from_template(system_message_content)] # Another option for some agents
    }

    try:
        documentation_agent = initialize_agent(
            tools=TOOLS,
            llm=llm,
            agent=AgentType.OPENAI_FUNCTIONS, # Changed to support multi-input tools
            verbose=config.get("agent.verbose", True),
            handle_parsing_errors=True, # Gracefully handle parsing errors
            agent_kwargs=agent_kwargs,
            max_iterations=config.get("agent.max_iterations", 15)
        )
        debugger.logger.info("Model Documentation Agent initialized successfully.")
        return documentation_agent
    except Exception as e:
        debugger.log_exception("create_documentation_agent", e, {"agent_type": "OPENAI_FUNCTIONS"})
        # Depending on desired behavior, either raise e or return None or a dummy agent
        raise RuntimeError(f"Failed to initialize the documentation agent: {str(e)}")

if __name__ == '__main__':
    # This is a simple test script that can be run to check agent initialization
    # In a real application, Config and ModelDocDebugger would be set up more centrally.
    
    print("Testing agent initialization...")
    test_config = Config() # Uses default config.py
    # Ensure API key is available for this test, e.g., via environment variable ANTHROPIC_API_KEY
    # or by setting it in a .env file loaded by python-dotenv if Config handles that.
    
    # For local testing, you might need to set a dummy API key if not making actual LLM calls
    # or ensure your environment is configured.
    # test_config.set("anthropic_api_key", "YOUR_ANTHROPIC_API_KEY_HERE_OR_SET_ENV_VAR")

    if not test_config.get("anthropic_api_key") and not os.getenv("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY not set in config or environment. LLM calls will fail.")
        # You might want to exit or use a mock LLM for offline testing.

    test_debugger = ModelDocDebugger(logger_name="AgentTest", debug_level="DEBUG", log_to_console=True)
    
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