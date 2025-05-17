from langchain.prompts import PromptTemplate as LangchainPromptTemplate # Alias original
from typing import Dict, Any

# Attempt to import debugger. If it fails, create a placeholder to avoid crashing.
# This allows prompts to be defined even if the full debug environment isn't set up.
# In a full application, a proper dependency injection or shared context would be better.
try:
    from ..debug.logger import ModelDocDebugger
    # Assuming a global/shared debugger instance for simplicity in this module
    # In a real app, this might be passed in or accessed via a global context
    debugger = ModelDocDebugger(logger_name="Prompts", debug_level="INFO")
except ImportError:
    # Placeholder debugger if the main one isn't available (e.g. during isolated testing of prompts)
    class PlaceholderDebugger:
        def log_prompt(self, prompt_name: str, template: str, variables: Dict[str, Any], rendered: str):
            # print(f"[PlaceholderDebug] Rendering prompt: {prompt_name}\nRendered: {rendered[:100]}...")
            pass # No-op if debugger not found
    debugger = PlaceholderDebugger()

class PromptTemplate(LangchainPromptTemplate):
    """Custom PromptTemplate wrapper to integrate with ModelDocDebugger."""
    
    def __init__(self, name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name # Store a name for this prompt for logging

    def format(self, **kwargs: Any) -> str:
        """Format the prompt with the MRO and log the details."""
        # Resolve a MRO issue if 'name' is in kwargs by mistake from a parent class
        # This ensures our 'name' attribute is used for logging, not one from kwargs
        prompt_name_for_log = self.name
        
        # Call the original format method
        rendered_prompt = super().format(**kwargs)
        
        # Log using the debugger instance
        if hasattr(debugger, 'log_prompt'): # Check if the real debugger is available
             debugger.log_prompt(
                prompt_name=prompt_name_for_log,
                template=self.template, 
                variables=kwargs, 
                rendered=rendered_prompt
            )
        return rendered_prompt

    # classmethod `from_template` needs to be overridden if we want it to return instances of this subclass
    @classmethod
    def from_template(cls, template: str, name: str = "UnnamedPrompt", **kwargs: Any):
        """Create a PromptTemplate from a string template, with a name for logging."""
        # This ensures that PromptTemplate.from_template() creates our custom class
        # and passes the name to its constructor.
        return cls(name=name, template=template, **kwargs)


# --- Prompts Definitions ---

# File summary prompt (generic)
prompt_file_summary = PromptTemplate.from_template(
    name="file_summary_v1", # Added name for logging
    template=(
        """
        You are a documentation assistant. Your task is to summarize the provided code file.
        Focus on its primary purpose, key inputs it processes, main outputs it generates, 
        and the core logic or algorithms it implements.

        File Content:
        ```{file_content}```

        Summary:
        """
    )
)

# Hierarchical summary prompt
prompt_hierarchical_summary = PromptTemplate.from_template(
    name="hierarchical_summary_v1",
    template=(
        """
        You are a documentation assistant. You have been provided with a collection of 
        summaries for individual code files or code chunks from a single codebase.
        Your task is to generate a higher-level summary that synthesizes these individual summaries.
        This higher-level summary should explain the overall architecture, key relationships, 
        dependencies, and main thematic groupings across these files/chunks.

        Individual Summaries:
        {summaries}

        Hierarchical Summary:
        """
    )
)

# Outline generation prompt (takes template sections)
prompt_outline_generation = PromptTemplate.from_template(
    name="outline_generation_v1",
    template=(
        """
        You are a documentation assistant. Given the following documentation template sections, 
        generate a draft outline for a technical document.
        For each section and subsection, provide a brief (1-2 sentence) description of the 
        content that should be included. Maintain the hierarchical structure if present in the input.

        Documentation Template Sections:
        {template_sections}

        Draft Outline:
        """
    )
)

# Section drafting prompt factory function
def create_section_drafting_prompt(section_name: str, section_description: str) -> PromptTemplate:
    """
    Creates a named PromptTemplate for drafting a specific documentation section.
    """
    # Sanitize section_name for use in prompt name (e.g., replace spaces, special chars)
    safe_prompt_name = f"section_draft_{section_name.lower().replace(' ', '_')}_v1"
    
    return PromptTemplate.from_template(
        name=safe_prompt_name,
        template=(
            f"""
            You are a documentation assistant. Your task is to draft the '{section_name}' section of a technical document.
            This section is described as: "{section_description}"

            To help you, here are relevant code summaries and selected code snippets from the codebase:
            ```
            {{summaries_and_snippets}} 
            ```
            
            Draft the '{section_name}' section based on its description and the provided context.
            Ensure the content is technically accurate, clear, and concise. 
            Use appropriate headings and prose. If the context is insufficient, state what is missing.

            Section Draft for '{section_name}':
            """
        )
    )

# Improvement suggestions prompt
prompt_improvement_suggestions = PromptTemplate.from_template(
    name="improvement_suggestions_v1",
    template=(
        """
        You are a documentation assistant and code quality analyst.
        Review the following generated documentation draft and the summaries of the underlying codebase.
        Provide actionable suggestions for improvements. Consider these areas:
        1.  **Documentation Gaps**: Missing information, unclear explanations, inconsistencies.
        2.  **Code Refactoring**: Opportunities for cleaner, more efficient, or more maintainable code based on its summary.
        3.  **Best Practices**: Adherence to coding standards or documentation principles.
        4.  **Further Analysis**: Areas that might require deeper investigation or more detailed documentation.

        Generated Documentation Draft:
        ```
        {documentation_draft}
        ```

        Codebase Summaries:
        ```
        {code_summaries}
        ```

        Improvement Suggestions:
        """
    )
)

# Example of how to use the section drafting prompt factory:
# prompt_methodology_section = create_section_drafting_prompt(
#     section_name="Methodology", 
#     section_description="Detailed explanation of algorithms, statistical methods, and implementation approach."
# )