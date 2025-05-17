# Design Recommendations for Model Documentation Agent

This document provides architectural and design recommendations to enhance the current Model Documentation Agent implementation to better align with the project requirements.

## 1. Architecture Improvements

### 1.1. Code Structure

#### Current Implementation
```
model-doc-agent/
├── src/
│   ├── data_loader.py   # File loading only
│   ├── prompts.py       # Basic prompt templates
│   ├── tools.py         # LangChain tool wrappers
│   ├── agent.py         # Simple agent executor
│   └── examples/
│       └── sample_run.py
```

#### Recommended Structure
```
model-doc-agent/
├── src/
│   ├── data/
│   │   ├── loader.py            # Enhanced code parser
│   │   ├── chunk_parser.py      # Function/class extraction
│   │   └── schema.py            # Data models and types
│   ├── indexing/
│   │   ├── index_builder.py     # Metadata-rich indexing
│   │   ├── section_mapper.py    # Map code to template sections
│   │   └── retriever.py         # Context-aware retrieval
│   ├── prompts/
│   │   ├── base.py              # Base prompt templates
│   │   ├── summary_prompts.py   # Summary generation prompts
│   │   ├── outline_prompts.py   # Outline generation prompts
│   │   └── section_prompts.py   # Section-specific prompts
│   ├── tools/
│   │   ├── summary_tools.py     # Summary generation tools
│   │   ├── outline_tools.py     # Outline generation tools
│   │   ├── section_tools.py     # Section drafting tools
│   │   └── analysis_tools.py    # Improvement suggestion tools
│   ├── agent/
│   │   ├── executor.py          # Agent implementation
│   │   ├── prompt_manager.py    # Dynamic prompt management
│   │   └── state_manager.py     # Session state tracking
│   ├── debug/
│   │   ├── logger.py            # Structured logging
│   │   ├── metrics.py           # Performance metrics
│   │   └── visualizer.py        # Debug visualizations
│   └── utils/
│       ├── config.py            # Configuration management
│       ├── exceptions.py        # Custom exceptions
│       └── validators.py        # Input validation
```

### 1.2. Data Flow Architecture

![Data Flow Architecture Diagram]

The recommended data flow should follow this pattern:

1. **Input Stage**
   - Load codebase files
   - Parse logical chunks (functions, classes)
   - Load documentation template

2. **Processing Stage**
   - Generate file-level summaries
   - Create chunk-level summaries
   - Build hierarchical summaries
   - Construct metadata-rich index

3. **Generation Stage**
   - Create section outlines
   - Draft section content using contextual retrieval
   - Review and refine drafts
   - Generate improvement suggestions

4. **Output Stage**
   - Format documentation
   - Export to desired format (MD, HTML, etc.)
   - Provide performance metrics

## 2. Component Enhancements

### 2.1. Enhanced Code Parser

Replace the current basic file loader with a more sophisticated parser:

```python
import ast
from typing import Dict, List, Any, Optional, Tuple

class CodeChunk:
    """Represents a logical chunk of code (function, class, method)."""
    
    def __init__(self, name: str, type: str, source: str, 
                 start_line: int, end_line: int,
                 parent: Optional['CodeChunk'] = None):
        self.name = name
        self.type = type  # 'function', 'class', 'method'
        self.source = source
        self.start_line = start_line
        self.end_line = end_line
        self.parent = parent
        self.children = []  # For methods within classes
        
    def add_child(self, child: 'CodeChunk'):
        """Add a child chunk (e.g., method to class)."""
        self.children.append(child)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            'name': self.name,
            'type': self.type,
            'source': self.source,
            'start_line': self.start_line,
            'end_line': self.end_line,
        }
        if self.children:
            result['children'] = [child.to_dict() for child in self.children]
        return result

class PythonCodeParser:
    """Enhanced Python code parser that extracts logical chunks."""
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a Python file into a structured representation.
        
        Returns:
        --------
        Dict with:
            - 'file_path': original path
            - 'content': full file content
            - 'chunks': list of CodeChunk objects
        """
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Parse into AST
        tree = ast.parse(content)
        source_lines = content.splitlines()
        
        # Extract top-level chunks
        chunks = []
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef):
                chunk = self._extract_function(node, source_lines)
                chunks.append(chunk)
            elif isinstance(node, ast.ClassDef):
                chunk = self._extract_class(node, source_lines)
                chunks.append(chunk)
                
        return {
            'file_path': file_path,
            'content': content,
            'chunks': [chunk.to_dict() for chunk in chunks]
        }
    
    def _extract_function(self, node: ast.FunctionDef, 
                          source_lines: List[str], 
                          parent: Optional[CodeChunk] = None) -> CodeChunk:
        """Extract a function definition."""
        start_line = node.lineno
        end_line = self._find_end_line(node, source_lines)
        source = '\n'.join(source_lines[start_line-1:end_line])
        
        return CodeChunk(
            name=node.name,
            type='method' if parent else 'function',
            source=source,
            start_line=start_line,
            end_line=end_line,
            parent=parent
        )
    
    def _extract_class(self, node: ast.ClassDef, source_lines: List[str]) -> CodeChunk:
        """Extract a class definition with its methods."""
        start_line = node.lineno
        end_line = self._find_end_line(node, source_lines)
        source = '\n'.join(source_lines[start_line-1:end_line])
        
        class_chunk = CodeChunk(
            name=node.name,
            type='class',
            source=source,
            start_line=start_line,
            end_line=end_line
        )
        
        # Extract methods
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_chunk = self._extract_function(item, source_lines, class_chunk)
                class_chunk.add_child(method_chunk)
                
        return class_chunk
    
    def _find_end_line(self, node: ast.AST, source_lines: List[str]) -> int:
        """Find the end line of a node by analyzing indentation."""
        start_line = node.lineno
        
        # Start from the line after the definition
        current_line = start_line
        while current_line < len(source_lines):
            # Skip empty lines or comments at the end of the definition
            if not source_lines[current_line].strip() or source_lines[current_line].strip().startswith('#'):
                current_line += 1
                continue
                
            # If we find a line with same or less indentation as the
            # definition line, we've reached the end
            if (current_line > start_line and 
                len(source_lines[current_line]) - len(source_lines[current_line].lstrip()) <= 
                len(source_lines[start_line-1]) - len(source_lines[start_line-1].lstrip())):
                return current_line
                
            current_line += 1
            
        return len(source_lines)
```

### 2.2. Metadata-Rich Index Builder

Add a new component for building a metadata-rich index:

```python
from typing import Dict, List, Any, Optional
import uuid

class DocumentSection:
    """Represents a section in the documentation template."""
    
    def __init__(self, id: int, title: str, description: str):
        self.id = id
        self.title = title
        self.description = description
        
class IndexEntry:
    """An entry in the metadata-rich index."""
    
    def __init__(self, 
                 source_file: str, 
                 chunk_name: Optional[str] = None,
                 chunk_type: Optional[str] = None,
                 summary: str = "",
                 relevance_score: float = 0.0):
        self.id = str(uuid.uuid4())
        self.source_file = source_file
        self.chunk_name = chunk_name
        self.chunk_type = chunk_type
        self.summary = summary
        self.relevance_score = relevance_score
        self.section_mappings = []  # List of (section_id, relevance_score) tuples
        
    def add_section_mapping(self, section_id: int, relevance_score: float):
        """Add a mapping to a documentation section."""
        self.section_mappings.append((section_id, relevance_score))
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'id': self.id,
            'source_file': self.source_file,
            'chunk_name': self.chunk_name,
            'chunk_type': self.chunk_type,
            'summary': self.summary,
            'relevance_score': self.relevance_score,
            'section_mappings': self.section_mappings
        }

class IndexBuilder:
    """Builds a metadata-rich index from code summaries."""
    
    def __init__(self, llm):
        self.llm = llm
        self.index_entries = []
        
    def build_index(self, 
                   parsed_files: List[Dict[str, Any]], 
                   summaries: Dict[str, str],
                   sections: List[DocumentSection]) -> List[IndexEntry]:
        """
        Build index mapping code chunks to documentation sections.
        
        Parameters:
        -----------
        parsed_files : List[Dict]
            Output from the CodeParser
        summaries : Dict
            File and chunk summaries
        sections : List[DocumentSection]
            Documentation template sections
            
        Returns:
        --------
        List[IndexEntry]: The constructed index
        """
        # Create index entries for each file and chunk
        for file_data in parsed_files:
            file_path = file_data['file_path']
            file_name = file_path.split('/')[-1]
            
            # Add file-level entry
            if file_name in summaries:
                file_entry = IndexEntry(
                    source_file=file_name,
                    summary=summaries[file_name],
                    relevance_score=1.0  # Full relevance for own summary
                )
                
                # Map to relevant sections
                self._map_to_sections(file_entry, sections)
                self.index_entries.append(file_entry)
            
            # Add chunk-level entries if available
            for chunk in file_data.get('chunks', []):
                chunk_id = f"{file_name}:{chunk['name']}"
                if chunk_id in summaries:
                    chunk_entry = IndexEntry(
                        source_file=file_name,
                        chunk_name=chunk['name'],
                        chunk_type=chunk['type'],
                        summary=summaries[chunk_id],
                        relevance_score=1.0
                    )
                    
                    # Map to relevant sections
                    self._map_to_sections(chunk_entry, sections)
                    self.index_entries.append(chunk_entry)
        
        return self.index_entries
    
    def _map_to_sections(self, entry: IndexEntry, sections: List[DocumentSection]):
        """Map an index entry to relevant documentation sections."""
        # Use LLM to determine relevance to each section
        for section in sections:
            # Create prompt to evaluate relevance
            prompt = f"""
            Given this code summary:
            "{entry.summary}"
            
            Evaluate its relevance to this documentation section:
            Section: {section.title}
            Description: {section.description}
            
            Rate relevance from 0.0 (not relevant) to 1.0 (highly relevant).
            Return only a single float value.
            """
            
            # Get relevance score from LLM
            try:
                relevance_text = self.llm(prompt)
                relevance_score = float(relevance_text.strip())
                
                # Ensure score is in valid range
                relevance_score = max(0.0, min(1.0, relevance_score))
                
                # If relevance exceeds threshold, add mapping
                if relevance_score >= 0.3:  # Minimum relevance threshold
                    entry.add_section_mapping(section.id, relevance_score)
            except:
                # Fall back to simple text matching if LLM call fails
                section_keywords = set(section.title.lower().split() + 
                                      section.description.lower().split())
                summary_words = set(entry.summary.lower().split())
                intersection = section_keywords.intersection(summary_words)
                
                if intersection:
                    relevance = len(intersection) / len(section_keywords)
                    entry.add_section_mapping(section.id, relevance)
```

### 2.3. State Management

Add session state management to maintain context between agent calls:

```python
import pickle
import json
import os
import time
from typing import Dict, Any, Optional, List

class SessionState:
    """Manages persistent state across agent invocations."""
    
    def __init__(self, session_id: Optional[str] = None, 
                 storage_dir: str = ".sessions"):
        """
        Initialize session state.
        
        Parameters:
        -----------
        session_id : str, optional
            Unique session identifier. If None, generates a new ID.
        storage_dir : str
            Directory to store session data
        """
        self.session_id = session_id or f"session_{int(time.time())}"
        self.storage_dir = storage_dir
        self.state = {
            'session_id': self.session_id,
            'created_at': time.time(),
            'modified_at': time.time(),
            'codebase': {},
            'template': {},
            'summaries': {},
            'index': [],
            'outlines': {},
            'drafts': {},
            'improvements': []
        }
        
        # Create storage directory if it doesn't exist
        os.makedirs(storage_dir, exist_ok=True)
        
        # Load existing session if provided
        if session_id:
            self.load_session()
    
    def save_session(self):
        """Save current session state to disk."""
        self.state['modified_at'] = time.time()
        file_path = os.path.join(self.storage_dir, f"{self.session_id}.json")
        
        with open(file_path, 'w') as f:
            json.dump(self.state, f, indent=2)
            
    def load_session(self):
        """Load session state from disk."""
        file_path = os.path.join(self.storage_dir, f"{self.session_id}.json")
        
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                self.state = json.load(f)
        else:
            raise ValueError(f"Session {self.session_id} does not exist")
    
    def update_codebase(self, codebase_data: Dict[str, Any]):
        """Update codebase information."""
        self.state['codebase'] = codebase_data
        self.save_session()
        
    def update_template(self, template_data: Dict[str, Any]):
        """Update template information."""
        self.state['template'] = template_data
        self.save_session()
        
    def update_summaries(self, summaries: Dict[str, str]):
        """Update file and chunk summaries."""
        self.state['summaries'].update(summaries)
        self.save_session()
        
    def update_index(self, index: List[Dict[str, Any]]):
        """Update metadata index."""
        self.state['index'] = index
        self.save_session()
        
    def update_outline(self, section_id: int, outline: str):
        """Update section outline."""
        self.state['outlines'][str(section_id)] = outline
        self.save_session()
        
    def update_draft(self, section_id: int, draft: str):
        """Update section draft."""
        self.state['drafts'][str(section_id)] = draft
        self.save_session()
        
    def add_improvement(self, improvement: str):
        """Add improvement suggestion."""
        self.state['improvements'].append({
            'timestamp': time.time(),
            'suggestion': improvement
        })
        self.save_session()
        
    def get_combined_draft(self) -> str:
        """Get combined draft of all sections."""
        # Sort sections by ID
        sorted_sections = sorted(
            self.state['drafts'].items(), 
            key=lambda x: int(x[0])
        )
        
        # Combine drafts
        combined = []
        for section_id, content in sorted_sections:
            # Get section title from template if available
            section_title = "Unknown Section"
            for section in self.state['template'].get('sections', []):
                if section.get('id') == int(section_id):
                    section_title = section.get('title', "Unknown Section")
                    break
                    
            combined.append(f"## {section_title}\n\n{content}\n")
            
        return "\n".join(combined)
```

### 2.4. Dynamic Prompt Management

Add a prompt manager for dynamic prompt inspection and modification:

```python
from typing import Dict, Any, List, Optional
from langchain.prompts import PromptTemplate

class PromptManager:
    """Manages dynamic prompt templates."""
    
    def __init__(self):
        self.templates = {}
        self.history = {}  # Track modifications
        
    def register_template(self, name: str, template: str, 
                         description: str = "", 
                         variables: List[str] = None):
        """
        Register a new prompt template.
        
        Parameters:
        -----------
        name : str
            Unique name for the template
        template : str
            The prompt template string
        description : str
            Description of the template's purpose
        variables : List[str]
            List of variable names used in the template
        """
        if name in self.templates:
            # Save history before overwriting
            if name not in self.history:
                self.history[name] = []
                
            self.history[name].append(self.templates[name])
            
        self.templates[name] = {
            'template': template,
            'description': description,
            'variables': variables or [],
            'created_at': time.time()
        }
        
    def get_template(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a prompt template by name."""
        return self.templates.get(name)
    
    def modify_template(self, name: str, new_template: str) -> bool:
        """
        Modify an existing template.
        
        Returns:
        --------
        bool: True if successful, False if template not found
        """
        if name not in self.templates:
            return False
            
        # Save history
        if name not in self.history:
            self.history[name] = []
            
        self.history[name].append(self.templates[name])
        
        # Update template
        self.templates[name]['template'] = new_template
        self.templates[name]['modified_at'] = time.time()
        
        return True
    
    def list_templates(self) -> List[str]:
        """List all available template names."""
        return list(self.templates.keys())
    
    def get_template_history(self, name: str) -> List[Dict[str, Any]]:
        """Get modification history for a template."""
        return self.history.get(name, [])
    
    def create_prompt_template(self, name: str) -> Optional[PromptTemplate]:
        """Create a LangChain PromptTemplate from a registered template."""
        if name not in self.templates:
            return None
            
        template_data = self.templates[name]
        
        return PromptTemplate.from_template(template_data['template'])
```

## 3. Integration Recommendations

### 3.1. Combining Components

The enhanced components should be integrated in a modular, extensible way:

```python
from typing import Dict, Any, List, Optional
import os

from src.data.loader import PythonCodeParser
from src.indexing.index_builder import IndexBuilder, DocumentSection
from src.agent.state_manager import SessionState
from src.agent.prompt_manager import PromptManager
from src.debug.logger import ModelDocDebugger

class ModelDocumentationAgent:
    """Main agent class integrating all components."""
    
    def __init__(self, llm, debug_level="INFO", session_id=None):
        """
        Initialize the documentation agent.
        
        Parameters:
        -----------
        llm : LLM
            Language model for generation
        debug_level : str
            Logging level for debugger
        session_id : str, optional
            Existing session ID to resume
        """
        # Initialize components
        self.llm = llm
        self.debugger = ModelDocDebugger(debug_level)
        self.code_parser = PythonCodeParser()
        self.index_builder = IndexBuilder(llm)
        self.state = SessionState(session_id)
        self.prompt_manager = PromptManager()
        
        # Register default prompts
        self._register_default_prompts()
        
    def _register_default_prompts(self):
        """Register default prompt templates."""
        # File summary prompt
        self.prompt_manager.register_template(
            name="file_summary",
            template="""
            You are a documentation assistant. Summarize the purpose, inputs, outputs, and key logic of this file:
            
            {file_content}
            """,
            description="Generates summary of code file",
            variables=["file_content"]
        )
        
        # Add other default prompts...
        
    def process_codebase(self, code_dir: str) -> Dict[str, Any]:
        """
        Process a codebase directory.
        
        Parameters:
        -----------
        code_dir : str
            Directory containing code files
            
        Returns:
        --------
        Dict with processing results
        """
        self.debugger.logger.info(f"Processing codebase: {code_dir}")
        
        # Parse code files
        parsed_files = []
        for root, _, files in os.walk(code_dir):
            for file in files:
                if file.endswith(('.py', '.js', '.java', '.c', '.cpp')):
                    file_path = os.path.join(root, file)
                    try:
                        parsed_file = self.code_parser.parse_file(file_path)
                        parsed_files.append(parsed_file)
                    except Exception as e:
                        self.debugger.log_exception(
                            "process_codebase", e, 
                            {"file": file_path}
                        )
        
        # Update session state
        self.state.update_codebase({
            'dir': code_dir,
            'files': [f['file_path'] for f in parsed_files]
        })
        
        return {
            'parsed_files': len(parsed_files),
            'chunks': sum(len(f.get('chunks', [])) for f in parsed_files)
        }
    
    def load_template(self, template_path: str) -> Dict[str, Any]:
        """Load documentation template."""
        try:
            with open(template_path, 'r') as f:
                template = json.load(f)
                
            # Update session state
            self.state.update_template(template)
            
            return {
                'name': template.get('name', 'Unknown Template'),
                'sections': len(template.get('sections', []))
            }
        except Exception as e:
            self.debugger.log_exception("load_template", e, {"path": template_path})
            raise
    
    def generate_summaries(self) -> Dict[str, Any]:
        """Generate summaries for all files and chunks."""
        # More implementation...
```

### 3.2. Advanced Agent Interface

Implement an enhanced agent interface with conversational capabilities:

```python
class ModelDocConversationAgent:
    """Conversational interface for the Model Documentation Agent."""
    
    def __init__(self, base_agent: ModelDocumentationAgent):
        """
        Initialize conversation agent.
        
        Parameters:
        -----------
        base_agent : ModelDocumentationAgent
            Core documentation agent
        """
        self.agent = base_agent
        self.conversation_history = []
        
    def process_message(self, message: str) -> str:
        """
        Process a user message and return a response.
        
        Parameters:
        -----------
        message : str
            User message
            
        Returns:
        --------
        str: Agent response
        """
        # Add to conversation history
        self.conversation_history.append({
            'role': 'user',
            'content': message,
            'timestamp': time.time()
        })
        
        # Process user intent
        intent = self._extract_intent(message)
        response = ""
        
        try:
            if intent.get('action') == 'summarize_codebase':
                code_dir = intent.get('code_dir', 'codebase/')
                result = self.agent.process_codebase(code_dir)
                summaries = self.agent.generate_summaries()
                response = f"Processed {result['parsed_files']} files with {result['chunks']} code chunks. Generated {len(summaries)} summaries."
                
            elif intent.get('action') == 'generate_outline':
                template_path = intent.get('template_path')
                if not template_path:
                    response = "Please specify a template path."
                else:
                    template_info = self.agent.load_template(template_path)
                    outlines = self.agent.generate_outlines()
                    response = f"Generated outlines for {len(outlines)} sections using template '{template_info['name']}'."
                    
            # More intent handlers...
                
            else:
                # Default to a general response
                response = "I'm not sure how to help with that. You can ask me to summarize code, generate outlines, or draft documentation sections."
                
        except Exception as e:
            self.agent.debugger.log_exception("process_message", e, {"message": message})
            response = f"Sorry, I encountered an error: {str(e)}"
            
        # Add to conversation history
        self.conversation_history.append({
            'role': 'assistant',
            'content': response,
            'timestamp': time.time()
        })
        
        return response
    
    def _extract_intent(self, message: str) -> Dict[str, Any]:
        """Extract user intent from message."""
        # Use LLM to extract structured intent from message
        prompt = f"""
        Extract the intent from this user message:
        "{message}"
        
        Return a JSON object with:
        - action: the primary action requested (e.g., summarize_codebase, generate_outline, draft_section)
        - parameters: any relevant parameters (e.g., code_dir, template_path, section_id)
        
        Example:
        {{
            "action": "summarize_codebase",
            "code_dir": "path/to/code"
        }}
        """
        
        try:
            result = self.agent.llm(prompt)
            # Parse JSON response
            intent = json.loads(result)
            return intent
        except:
            # Fall back to keyword matching
            intent = {'action': 'unknown'}
            
            if 'summarize' in message.lower() and ('code' in message.lower() or 'file' in message.lower()):
                intent['action'] = 'summarize_codebase'
                # Try to extract code_dir
                if 'in' in message.lower() and 'dir' in message.lower():
                    parts = message.split('in')
                    if len(parts) > 1:
                        possible_dir = parts[1].strip().split()[0].strip()
                        if possible_dir:
                            intent['code_dir'] = possible_dir
            
            # More keyword-based intent extraction...
                
            return intent
```

## 4. Implementation Roadmap

### Phase 1: Core Architecture Improvements
1. Refactor code structure to modular architecture
2. Implement chunk-level code parsing
3. Add session state management
4. Develop debug infrastructure

### Phase 2: Enhanced Functionality
1. Build metadata-rich index with section mapping
2. Implement dynamic prompt management
3. Add conversational agent interface
4. Enhance error handling and validation

### Phase 3: Advanced Features
1. Integrate vector embeddings for semantic search
2. Add multi-format output options
3. Implement template library management
4. Develop visualization and analysis tools

## 5. Conclusion

The proposed design enhancements provide a solid path to evolve the current implementation into a robust, production-ready documentation agent. Key improvements in code parsing, metadata indexing, state management, and conversational capabilities will help meet all the requirements in the project documentation.

By adopting a modular, component-based architecture, the system will be easier to maintain, test, and extend with new capabilities in the future. 