import logging
import time
from functools import wraps
from typing import Dict, Any, Callable, Optional, List

# Configure basic logging
# Applications can reconfigure this if needed
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class ModelDocDebugger:
    """Debug manager for Model Documentation Agent."""
    
    def __init__(self, logger_name: str = "ModelDocAgent", debug_level: str = "INFO"):
        """
        Initialize debugger with specified level.
        
        Parameters:
        -----------
        logger_name : str
            Name for the logger instance.
        debug_level : str
            Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.logger = logging.getLogger(logger_name)
        self.set_level(debug_level)
        self.execution_times: Dict[str, List[float]] = {}
        self.step_count: int = 0
        self.current_session: str = time.strftime("%Y%m%d-%H%M%S")
        
    def set_level(self, level: str):
        """Set the logging level."""
        numeric_level = getattr(logging, level.upper(), None)
        if not isinstance(numeric_level, int):
            self.logger.warning(f"Invalid log level: {level}. Defaulting to INFO.")
            numeric_level = logging.INFO
        self.logger.setLevel(numeric_level)
        
    def log_tool_call(self, tool_name: str, inputs: Dict[str, Any], outputs: Any):
        """Log a tool call with inputs and outputs."""
        self.step_count += 1
        self.logger.info(f"STEP {self.step_count}: Tool '{tool_name}' called")
        self.logger.debug(f"Tool inputs: {inputs}")
        
        if isinstance(outputs, str) and len(outputs) > 500:
            self.logger.debug(f"Tool output: {outputs[:500]}... [truncated, total length: {len(outputs)}]")
        elif isinstance(outputs, dict) or isinstance(outputs, list):
            try:
                import json
                output_str = json.dumps(outputs, indent=2, default=str) # Use default=str for non-serializable
                if len(output_str) > 500:
                     self.logger.debug(f"Tool output (JSON): {output_str[:500]}... [truncated, total length: {len(output_str)}]")
                else:
                    self.logger.debug(f"Tool output (JSON): {output_str}")
            except TypeError:
                 self.logger.debug(f"Tool output (non-serializable): {str(outputs)[:500]}...") # Fallback for complex objects
        else:
            self.logger.debug(f"Tool output: {outputs}")
    
    def log_prompt(self, prompt_name: str, template: str, variables: Dict[str, Any], rendered: str):
        """Log prompt rendering details."""
        self.logger.info(f"Rendering prompt: '{prompt_name}'")
        self.logger.debug(f"Template for '{prompt_name}':\n{template}")
        self.logger.debug(f"Variables for '{prompt_name}': {variables}")
        self.logger.debug(f"Rendered prompt '{prompt_name}':\n{rendered}")
    
    def log_exception(self, func_name: str, exception: Exception, context: Optional[Dict] = None):
        """Log detailed exception information."""
        self.logger.error(f"Exception in '{func_name}': {str(exception)}", exc_info=True)
        if context:
            self.logger.error(f"Context for '{func_name}' exception: {context}")
    
    def time_function(self, func: Callable) -> Callable:
        """Decorator to time function execution."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            func_name = func.__name__
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                self.log_exception(func_name, e, {"args": args, "kwargs": kwargs})
                raise # Re-raise the exception after logging
            finally:
                elapsed_time = time.time() - start_time
                if func_name not in self.execution_times:
                    self.execution_times[func_name] = []
                self.execution_times[func_name].append(elapsed_time)
                self.logger.debug(f"Function '{func_name}' took {elapsed_time:.4f} seconds")
        return wrapper
    
    def get_performance_summary(self) -> Dict[str, Dict[str, Any]]:
        """Generate performance summary for all timed functions."""
        summary: Dict[str, Dict[str, Any]] = {}
        for func_name, times in self.execution_times.items():
            summary[func_name] = {
                "calls": len(times),
                "total_time": sum(times),
                "avg_time": sum(times) / len(times) if times else 0,
                "min_time": min(times) if times else 0,
                "max_time": max(times) if times else 0
            }
        return summary

    def get_callback_handler(self):
        """Returns a LangChain callback handler for this debugger."""
        from langchain.callbacks.base import BaseCallbackHandler

        class DebuggerCallbackHandler(BaseCallbackHandler):
            def __init__(self, debugger_instance: ModelDocDebugger):
                self.debugger = debugger_instance

            def on_tool_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any) -> None:
                tool_name = serialized.get("name", "Unknown Tool")
                self.debugger.step_count +=1 # Increment step count here as well for agent context
                self.debugger.logger.info(f"AGENT STEP {self.debugger.step_count}: Starting Tool '{tool_name}'")
                self.debugger.logger.debug(f"Tool '{tool_name}' inputs: {inputs}")

            def on_tool_end(self, outputs: str, name: str, **kwargs: Any) -> None:
                self.debugger.logger.info(f"AGENT STEP {self.debugger.step_count}: Finished Tool '{name}'")
                if isinstance(outputs, str) and len(outputs) > 500:
                    self.debugger.logger.debug(f"Tool '{name}' output: {outputs[:500]}... [truncated, total length: {len(outputs)}]")
                else:
                    self.debugger.logger.debug(f"Tool '{name}' output: {outputs}")
            
            def on_tool_error(self, error: BaseException, name: str, **kwargs: Any) -> None:
                self.debugger.logger.error(f"AGENT STEP {self.debugger.step_count}: Error in Tool '{name}': {error}", exc_info=True)

            def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> None:
                self.debugger.logger.info("LLM call starting...")
                for i, prompt_text in enumerate(prompts):
                    self.debugger.log_prompt(f"llm_call_prompt_{i}", "N/A (Raw Prompt)", {}, prompt_text)

            def on_llm_end(self, response: Any, **kwargs: Any) -> None:
                self.debugger.logger.info("LLM call finished.")
                # Response object structure can vary, adapt as needed
                # For ChatAnthropic, it might be response.content
                self.debugger.logger.debug(f"LLM response: {str(response)[:500]}...")

            def on_llm_error(self, error: BaseException, **kwargs: Any) -> None:
                self.debugger.logger.error(f"Error in LLM call: {error}", exc_info=True)
            
            def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any) -> None:
                chain_name = serialized.get("name", serialized.get("id", ["Unknown Chain"])[-1])
                self.debugger.logger.info(f"Chain '{chain_name}' starting.")
                self.debugger.logger.debug(f"Chain '{chain_name}' inputs: {inputs}")

            def on_chain_end(self, outputs: Dict[str, Any], name: str = None, **kwargs: Any) -> None:
                chain_name = name or "Unknown Chain"
                self.debugger.logger.info(f"Chain '{chain_name}' finished.")
                self.debugger.logger.debug(f"Chain '{chain_name}' outputs: {outputs}")

            def on_chain_error(self, error: BaseException, name: str = None, **kwargs: Any) -> None:
                chain_name = name or "Unknown Chain"
                self.debugger.logger.error(f"Error in Chain '{chain_name}': {error}", exc_info=True)

        return DebuggerCallbackHandler(self)

# Example of a global debugger instance, can be imported and used across modules
# global_debugger = ModelDocDebugger() 