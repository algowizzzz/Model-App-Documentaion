# BMO Model Documentation Agent: Prompt Engineering and Workflow

**Version:** 1.0
**Date:** 2025-05-17
**Objective:** To outline the prompt design philosophy, specific prompts, and the operational workflow of the BMO AI Documentation Assistant for generating professional, regulator-ready documentation for models and code.

## 1. Guiding Persona: BMO AI Documentation Assistant

All prompts are engineered to instruct the Large Language Model (LLM) to adopt the persona of a **BMO AI Documentation Assistant for Models and Code**. This persona embodies the following characteristics:

*   **Professionalism & Formality:** Utilizes clear, crisp, formal business English suitable for BMO standards.
*   **Precision & Accuracy:** Strives for technical correctness and avoids ambiguity.
*   **Thoroughness & Comprehensiveness:** Aims to cover all necessary aspects required for regulatory scrutiny (e.g., SR 11-7, OSFI E-23 principles), internal model validation, and audit.
*   **Structured Thinking:** Organizes information logically and adheres to predefined templates and outlines.
*   **Analytical Acumen:** Not only describes but also analyzes code and model structure to synthesize insights (e.g., model-level assumptions, data flows).
*   **Risk & Compliance Aware:** Implicitly understands the importance of documenting assumptions, limitations, controls, and governance aspects.

## 2. Core Documentation Template

The primary driver for the documentation structure is the `templates/bmo_model_documentation_template.json` file. This JSON template defines:

*   **Document Metadata Fields:** Standard fields for document control (e.g., Document ID, Model Version, Authors, Approvers).
*   **Sections and Subsections:** A comprehensive list of sections (e.g., Executive Summary, Introduction, Model Methodology, Data, Implementation, Validation, Governance) and their respective subsections, each with a title, ID, and description of its purpose.
*   **Requirements:** Indicates mandatory sections and provides context for the type of information expected in each.

## 3. Key Prompts and Their Roles

The system utilizes a series of chained prompts to progressively analyze the codebase and generate the documentation.

### 3.1. `prompt_file_summary`

*   **Purpose:** To generate a detailed and structured summary for *each individual code file* in the target codebase.
*   **Persona Invocation:** "You are the BMO AI Documentation Assistant for Models and Code..."
*   **Key Input Variables:**
    *   `file_path`: The path to the code file being analyzed.
    *   `content`: The full content of the code file.
*   **Core Instructions & Expected Output:**
    *   Analyze the file meticulously according to BMO standards.
    *   Produce a structured summary covering:
        1.  **Overall Purpose and Role:** File's primary purpose and its specific role in the broader model/system.
        2.  **Key Components and Functionality:** List of major classes/functions with their purpose, operations, inputs, and outputs.
        3.  **Core Algorithms and Logic:** Description of core algorithms and complex logic.
        4.  **Data Structures:** Identification of significant internal data structures.
        5.  **Dependencies:** Internal (within codebase) and external (libraries) dependencies.
        6.  **Error Handling and Logging:** Description of observed mechanisms.
        7.  **Assumptions and Limitations (File-Specific):** File-specific assumptions and limitations.
    *   Output must follow this 7-point structure with clear headings.
*   **Role in Workflow:** Provides the foundational, granular analysis of each code component.

### 3.2. `prompt_hierarchical_summary`

*   **Purpose:** To synthesize a comprehensive, model-centric hierarchical summary from the collection of individual file summaries.
*   **Persona Invocation:** "You are the BMO AI Documentation Assistant for Models and Code..."
*   **Key Input Variables:**
    *   `file_summaries`: A collection of all summaries generated by `prompt_file_summary`.
*   **Core Instructions & Expected Output:**
    *   Construct a hierarchical summary elucidating the model's overall architecture and functionality, suitable for formal BMO model documentation.
    *   The summary must cover:
        1.  **Overall Model Purpose and Design Philosophy.**
        2.  **Key Functional Blocks/Modules:** Group related files, define block purpose, and list constituent files.
        3.  **Data Flow and Processing Sequence:** End-to-end data flow and transformations.
        4.  **Control Flow and Orchestration:** Execution flow and main driver logic.
        5.  **Key Inter-Module Dependencies and Interactions.**
        6.  **Significant Architectural Patterns or Design Choices.**
        7.  **Synthesized Model-Level Assumptions and Limitations:** Inferred from collective file summaries.
    *   Output must be a coherent narrative structured with clear headings for these 7 points.
*   **Role in Workflow:** Creates the primary contextual understanding of the entire codebase/model, which feeds into subsequent outlining and drafting stages.

### 3.3. `prompt_outline_generation`

*   **Purpose:** To generate a highly detailed, actionable preliminary outline for the full documentation, based on the `bmo_model_documentation_template.json` and the `hierarchical_model_summary`.
*   **Persona Invocation:** "You are the BMO AI Documentation Assistant for Models and Code..."
*   **Key Input Variables:**
    *   `template`: The JSON string of `bmo_model_documentation_template.json`.
    *   `codebase_summary`: The text of the hierarchical model summary.
*   **Core Instructions & Expected Output:**
    *   For *each* section and subsection in the input template:
        1.  Reiterate its title and template description.
        2.  List specific bullet points, questions to be answered, or topics to be elaborated upon during detailed drafting, drawing connections to the `codebase_summary`.
        3.  Note if information is missing in the summary and needs further investigation.
        4.  Note cross-references to other sections if applicable.
    *   Focus on linking methodology to implementation, detailing assumptions/limitations, data flow, and controls.
    *   Output should be a structured, nested text mirroring the template, serving as a blueprint for drafting.
*   **Role in Workflow:** Translates the high-level template structure and the codebase understanding into a specific, point-by-point plan for content creation for each document section.

### 3.4. `create_section_drafting_prompt` (Function that returns a `PromptTemplate`)

*   **Purpose:** To dynamically generate a prompt for drafting the content of a *specific section or subsection* of the documentation.
*   **Persona Invocation:** "As the BMO AI Documentation Assistant for Models and Code..."
*   **Key Input Variables (for the returned `PromptTemplate`):
    *   `section_schema`: The JSON schema (title, description, etc.) for the specific section/subsection from `bmo_model_documentation_template.json`.
    *   `detailed_outline_for_section`: The full detailed document outline generated by `prompt_outline_generation`. The LLM is expected to focus on parts relevant to the current section.
    *   `hierarchical_model_summary`: The comprehensive hierarchical summary of the model.
    *   `relevant_file_summaries`: A collection of individual file summaries (currently, all file summaries are passed).
*   **Core Instructions & Expected Output (for the LLM executing the generated prompt):**
    1.  **Address All Outline Points:** Methodically address points from `detailed_outline_for_section` relevant to the current section.
    2.  **Utilize Summaries:** Draw from hierarchical and relevant file summaries for context and specifics.
    3.  **Adhere to Section Schema:** Align with the purpose and scope defined in `section_schema`.
    4.  **Clarity, Precision, Professional Tone.**
    5.  **Completeness:** If information is unavailable in summaries, state this explicitly (e.g., "[Information regarding X needs to be sourced...]").
    6.  **Structure and Formatting:** Organize logically, use lists/subheadings as appropriate.
    *   The output is the drafted text content for that specific section/subsection.
*   **Role in Workflow:** This is the workhorse for content generation, taking the detailed plan from the outline phase and the analyzed codebase information to write the body of the document, section by section.

## 4. Documentation Generation Workflow

The end-to-end process is orchestrated by `test_end_to_end_summarization.py` (for generating intermediate artifacts) and `generate_final_documentation.py` (for producing the final Markdown document).

1.  **Initialization:**
    *   Load the `bmo_model_documentation_template.json`.
    *   Prepare placeholder document control metadata.

2.  **File Summarization (using `summarize_codebase_files` tool):**
    *   The `summarize_codebase_files` tool iterates through each file in the target codebase.
    *   For each file, it invokes an LLM call using the `prompt_file_summary`.
    *   **Output:** A collection of detailed file summaries (`02_file_summaries/` and `02_all_summaries.txt`).

3.  **Hierarchical Model Summarization (using `generate_hierarchical_summary` function):
    *   This function takes all individual file summaries as input.
    *   It invokes an LLM call using the `prompt_hierarchical_summary`.
    *   **Output:** A single text file containing the comprehensive hierarchical model summary (`03_hierarchical_summary.txt`).

4.  **Detailed Documentation Outline Generation (direct LLM call in `test_end_to_end_summarization.py`):
    *   Inputs: The `bmo_model_documentation_template.json` (as a string) and the `hierarchical_model_summary`.
    *   An LLM is invoked with `prompt_outline_generation`.
    *   **Output:** A detailed, structured textual outline, saved as `04_documentation_outline.json` (if valid JSON) or `04_documentation_outline.txt`.

5.  **Full Documentation Draft Generation (direct LLM calls in `test_end_to_end_summarization.py`):
    *   The script iterates through each section and subsection defined in `bmo_model_documentation_template.json`.
    *   For each section/subsection:
        *   The `create_section_drafting_prompt` function generates a tailored prompt.
        *   Inputs to this prompt include the section's schema, the entire detailed document outline (from step 4), the hierarchical model summary, and all file summaries.
        *   An LLM is invoked with this tailored prompt.
        *   The drafted content for the section/subsection is collected.
    *   **Output:** A JSON file (`05_full_documentation.json`) containing the template structure populated with the drafted content for all sections, including the document control metadata.

6.  **Summary Report Generation:**
    *   A JSON report (`06_summary_report.json`) is created, logging metadata about the generation run (timestamp, codebase directory, template used, files processed, sections generated).

7.  **Final Markdown Document Generation (using `generate_final_documentation.py`):
    *   This script reads:
        *   `01_template.json` (the copy of the BMO template used for the run).
        *   `05_full_documentation.json` (containing the drafted content and metadata).
        *   `06_summary_report.json` (for run metadata).
    *   It iterates through the template structure and the drafted content, formatting it into a single Markdown file.
    *   This includes generating a Table of Contents and a Document Control section.
    *   **Output:** `final_documentation.md` in the run-specific output directory.

## 5. Future Enhancements Considerations

*   **Smarter Contextualization for Section Drafting:** Instead of passing all file summaries or the entire document outline to each section drafting prompt, develop mechanisms to pass only the most relevant excerpts.
*   **Feedback Loop & Iterative Refinement:** Incorporate a mechanism for human review and feedback on drafts, potentially feeding this back to the LLM for revisions (e.g., using `prompt_improvement_suggestions`).
*   **Automated Diagram Generation:** Explore integration with tools or prompts that can generate conceptual diagrams (e.g., data flow, architecture) from the codebase summaries.
*   **Dynamic Content Linking:** Improve cross-referencing within the final Markdown document.

This document outlines the current enhanced prompt engineering strategy. It will be updated as the system evolves. 