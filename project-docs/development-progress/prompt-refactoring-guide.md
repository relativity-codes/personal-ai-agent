
# Breaking Change: Prompt Management Refactoring

This document outlines the recent refactoring of how system prompts are managed within the application. This was a significant change that moves our prompts from being hardcoded in Python to being dynamically loaded from dedicated markdown files.

## 1. Summary of Changes

- **Prompts moved to separate files:** All system prompts have been extracted from `backend/app/core/prompts.py` and are now located in the `backend/system_prompts/` directory.
- **Dynamic prompt loading:** The `backend/app/core/prompts.py` module has been updated to dynamically read these prompt files at runtime.
- **New directory structure:** A new directory, `backend/system_prompts/`, has been created to house the prompt files, organized by agent type.

## 2. Rationale for the Change

The previous approach of hardcoding prompts as large string literals in a Python file had several drawbacks:

- **Poor Readability:** It was difficult to read and edit prompts, especially complex ones with specific formatting.
- **Difficult to Version:** Tracking changes to prompts was cumbersome within a large Python file.
- **Mixing Logic and Content:** It mixed the application's logic with the LLM's instructional content.

The new system addresses these issues by:

- **Improving Maintainability:** Prompts are now in easy-to-edit Markdown files.
- **Decoupling Prompts from Code:** The prompt content is no longer part of the application's code.
- **Enhancing Collaboration:** It's easier for team members, including non-developers, to review and suggest changes to prompts.

## 3. New Folder Structure

The new folder structure for prompts is as follows:

```
backend/
└── system_prompts/
    ├── action/
    │   ├── calendar_parser.md
    │   ├── MY_GITHUB_parser.md
    │   ├── gmail_parser.md
    │   └── notion_parser.md
    ├── intent/
    │   ├── classifier.md
    │   └── validator.md
    └── managerial/
        ├── response_aggregator.md
        └── task_decomposer.md
```

## 4. How It Works

The `backend/app/core/prompts.py` file now contains a utility function, `_read_prompt`, which constructs the file path to a given prompt and reads its content. The prompts are then exported as constants, just as they were before, making this a non-breaking change for the rest of the application that consumes them.

```python
# backend/app/core/prompts.py

def _read_prompt(agent_type: str, prompt_name: str) -> str:
    '''Reads the content of a prompt file.'''
    # ... logic to build path and read file ...

# The constants are still available application-wide
INTENT_CLASSIFIER_PROMPT = _read_prompt("intent", "classifier")
```

## 5. How to Modify a Prompt

To modify a system prompt, simply locate the corresponding `.md` file in the `backend/system_prompts/` directory and edit it. Your changes will be reflected in the application automatically on the next run. **There is no longer any need to edit `backend/app/core/prompts.py` to change the content of a prompt.**

