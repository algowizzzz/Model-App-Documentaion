# Documentation Templates and Prompts

This directory contains templates and prompts used for code summarization and documentation generation.

## Base Prompts

Located in `src/prompts/base_prompts.py`:

### 1. File Summary Prompt
- **Name**: `prompt_file_summary`
- **Purpose**: Generates summaries for individual code files
- **Key Focus Areas**:
  - Main purpose of the file
  - Key components (functions, classes, methods)
  - Important relationships or dependencies
  - Notable algorithms or patterns

### 2. Hierarchical Summary Prompt
- **Name**: `prompt_hierarchical_summary`
- **Purpose**: Creates a consolidated summary of multiple files
- **Key Focus Areas**:
  - Groups related files and components
  - Identifies main modules and purposes
  - Explains relationships between parts
  - Highlights overall architecture

### 3. Documentation Outline Prompt
- **Name**: `prompt_outline_generation`
- **Purpose**: Generates documentation outlines from templates
- **Key Focus Areas**:
  - Follows template structure
  - Incorporates codebase information
  - Identifies sections for expansion
  - Suggests appropriate content

## Templates

### 1. Custom Summary Template
- **File**: `templates/custom_summary_template.json`
- **Purpose**: Defines structure for code summaries
- **Sections**:
  - Overview (with Purpose and Architecture subsections)
  - Key Components (with Classes and Functions subsections)
  - Component Relationships

### 2. Valid Template Example
- **File**: `templates/valid_template.json`
- **Purpose**: Example of a correctly formatted template
- **Sections**:
  - Overview
  - Implementation Details
  - Testing

### 3. Invalid Template Example
- **File**: `templates/invalid_template.json`
- **Purpose**: Example of incorrect template formatting
- **Note**: Used for testing template validation

## Usage in Summarization Process

1. **File-Level Summarization**:
   - Uses `prompt_file_summary`
   - Input: Individual code files
   - Output: Detailed summaries of each file

2. **Hierarchical Summarization**:
   - Uses `prompt_hierarchical_summary`
   - Input: Collection of file summaries
   - Output: Consolidated, structured overview

3. **Template-Based Documentation**:
   - Uses custom templates (e.g., `custom_summary_template.json`)
   - Uses `prompt_outline_generation`
   - Organizes summaries according to template structure

## File Locations

```
project_root/
├── src/
│   └── prompts/
│       └── base_prompts.py       # Contains all base prompts
└── templates/
    ├── README.md                 # This file
    ├── custom_summary_template.json
    ├── valid_template.json
    └── invalid_template.json
```

## Customization

To create new templates:
1. Use the structure shown in `custom_summary_template.json`
2. Define sections and subsections as needed
3. Include metadata (author, version, description)
4. Ensure all required sections are marked 