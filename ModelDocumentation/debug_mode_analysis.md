# Debug Mode Analysis for Model Documentation Agent

This document details the current state of debugging capabilities in the Model Documentation Agent and provides recommendations for implementing a proper debug mode.

## 1. Current State Assessment

The current implementation has limited debugging capabilities:

- `verbose=True` is set in the agent initialization, which provides basic LangChain execution tracing
- No structured logging or debug levels
- No ability to inspect intermediate results or decision-making process
- No mechanism to trace prompt rendering or template variable substitution
- No performance metrics or execution time tracking

## 2. Key Debug Mode Requirements

An effective debug mode for the Model Documentation Agent should provide:

### 2.1. Execution Tracing

- **Tool Selection Visibility**: Show why the agent chose specific tools
- **Prompt Rendering**: Display the actual prompts sent to Claude after variable substitution
- **Response Parsing**: Show how agent parses Claude's responses into actions
- **Step-by-Step Execution**: Track the sequence of operations with timestamps

### 2.2. Data Inspection

- **Intermediate Results**: View summaries, indices, and draft sections during generation
- **Template Validation**: Verify template structure and detect missing sections
- **Code Parsing Results**: Inspect how files are parsed into chunks (when implemented)
- **Context Windows**: Monitor token usage and context window management

### 2.3. Error Handling and Diagnostics

- **Exception Capturing**: Detailed error information without breaking execution
- **Warning System**: Flag potential issues (e.g., unusually short summaries)
- **Input Validation**: Verify that inputs meet expected formats and constraints
- **Recovery Suggestions**: Recommend fixes for common errors

## 3. Implementation Recommendations

### 3.1. Debug Module Addition

Create a new `debug.py` module with the following components:

```python
import logging
import time
from functools import wraps
from typing import Dict, Any, Callable, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class ModelDocDebugger:
    """Debug manager for Model Documentation Agent."""
    
    def __init__(self, debug_level: str = "INFO"):
        """
        Initialize debugger with specified level.
        
        Parameters:
        -----------
        debug_level : str
            Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self.logger = logging.getLogger("ModelDocAgent")
        self.debug_level = debug_level
        self.set_level(debug_level)
        self.execution_times = {}
        self.step_count = 0
        self.current_session = time.strftime("%Y%m%d-%H%M%S")
        
    def set_level(self, level: str):
        """Set the logging level."""
        numeric_level = getattr(logging, level.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError(f"Invalid log level: {level}")
        self.logger.setLevel(numeric_level)
        
    def log_tool_call(self, tool_name: str, inputs: Dict[str, Any], outputs: Any):
        """Log a tool call with inputs and outputs."""
        self.step_count += 1
        self.logger.info(f"STEP {self.step_count}: Tool '{tool_name}' called")
        self.logger.debug(f"Tool inputs: {inputs}")
        
        # For large outputs, summarize rather than logging entire content
        if isinstance(outputs, str) and len(outputs) > 500:
            self.logger.debug(f"Tool output: {outputs[:500]}... [truncated, total length: {len(outputs)}]")
        else:
            self.logger.debug(f"Tool output: {outputs}")
    
    def log_prompt(self, prompt_name: str, template: str, variables: Dict[str, Any], rendered: str):
        """Log prompt rendering details."""
        self.logger.info(f"Rendering prompt: {prompt_name}")
        self.logger.debug(f"Template: {template}")
        self.logger.debug(f"Variables: {variables}")
        self.logger.debug(f"Rendered prompt: {rendered}")
    
    def log_exception(self, func_name: str, exception: Exception, context: Optional[Dict] = None):
        """Log detailed exception information."""
        self.logger.error(f"Exception in {func_name}: {str(exception)}")
        if context:
            self.logger.error(f"Context: {context}")
        import traceback
        self.logger.error(traceback.format_exc())
    
    def time_function(self, func: Callable) -> Callable:
        """Decorator to time function execution."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed_time = time.time() - start_time
                func_name = func.__name__
                if func_name not in self.execution_times:
                    self.execution_times[func_name] = []
                self.execution_times[func_name].append(elapsed_time)
                self.logger.debug(f"Function {func_name} took {elapsed_time:.2f} seconds")
                return result
            except Exception as e:
                elapsed_time = time.time() - start_time
                self.log_exception(func.__name__, e, {"args": args, "kwargs": kwargs})
                raise
        return wrapper
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Generate performance summary for all timed functions."""
        summary = {}
        for func_name, times in self.execution_times.items():
            summary[func_name] = {
                "calls": len(times),
                "total_time": sum(times),
                "avg_time": sum(times) / len(times) if times else 0,
                "min_time": min(times) if times else 0,
                "max_time": max(times) if times else 0
            }
        return summary
```

### 3.2. Integration into Existing Modules

Modify the existing code to utilize the debug module:

1. **In `agent.py`:**
```python
from .debug import ModelDocDebugger

# Initialize debugger
debugger = ModelDocDebugger(debug_level="INFO")  # Could be set from config

# Modify agent initialization to use debug callbacks
agent = initialize_agent(
    tools=TOOLS,
    agent=AgentType.OPENAI_FUNCTIONS,
    llm=llm,
    system_message=system_message,
    verbose=True,
    callbacks=[debugger.get_callback_handler()]  # Add debug callbacks
)
```

2. **In `tools.py`:**
```python
from .debug import debugger

# Wrap each tool function with time_function decorator
@debugger.time_function
def summarize_files(code_dir: str) -> Dict[str, str]:
    try:
        files = load_codebase(code_dir)
        # Log loaded files
        debugger.logger.debug(f"Loaded {len(files)} files from {code_dir}")
        
        summaries = {}
        for fname, content in files.items():
            # Log each file being summarized
            debugger.logger.debug(f"Summarizing file: {fname}")
            summaries[fname] = LLMChain(llm=llm, prompt=prompt_file_summary).run(file_content=content)
        return summaries
    except Exception as e:
        debugger.log_exception("summarize_files", e, {"code_dir": code_dir})
        raise
```

3. **In `prompts.py`:**
```python
from .debug import debugger

# Create a wrapped version of PromptTemplate that logs rendering
class DebugPromptTemplate(PromptTemplate):
    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
    
    def format(self, **kwargs):
        rendered = super().format(**kwargs)
        debugger.log_prompt(self.name, self.template, kwargs, rendered)
        return rendered

# Replace prompt definitions with debug versions
prompt_file_summary = DebugPromptTemplate(
    name="file_summary",
    template="""
You are a documentation assistant. Summarize the purpose, inputs, outputs, and key logic of this file:

{file_content}
"""
)
```

### 3.3. Debug Command Interface

Add a debug interface to the agent that can be activated via:

```python
# Enable specific debug features
agent.run("Set debug level to DEBUG")
agent.run("Show performance metrics")
agent.run("Export debug logs to file")
agent.run("Replay last debug session")
```

### 3.4. Debug Visualization

Create debug visualizations for complex relationships:

1. **Dependency Graph**: Show relationships between files
2. **Section Mapping Heatmap**: Visualize which files map to which sections
3. **Execution Timeline**: Show sequence and duration of operations

## 4. Implementation Priorities

1. **Phase 1 (Core Debugging)**
   - Basic logging integration
   - Function timing
   - Exception handling

2. **Phase 2 (Enhanced Debug Tools)**
   - Prompt tracing
   - Interactive debug commands
   - Performance metrics

3. **Phase 3 (Advanced Diagnostics)**
   - Dependency visualization
   - Token usage tracking
   - Automated test generation

## 5. Conclusion

Adding a comprehensive debug mode is critical for developing and maintaining a complex documentation agent. The proposed implementation provides visibility into the agent's operation, tools for diagnosing issues, and metrics for performance optimization.

By prioritizing the debug infrastructure now, future development will be more efficient and the system will be more maintainable as complexity increases. 