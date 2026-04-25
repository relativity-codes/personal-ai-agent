import os

# The directory of the current file (prompts.py) -> backend/app/core
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# The project root directory -> backend/
_BACKEND_DIR = os.path.dirname(os.path.dirname(_CURRENT_DIR))
# The prompt directory
_PROMPT_DIR = os.path.join(_BACKEND_DIR, "system_prompts")


def _read_prompt(agent_type: str, prompt_name: str) -> str:
    '''Reads the content of a prompt file.'''
    file_path = os.path.join(_PROMPT_DIR, agent_type, f"{prompt_name}.md")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: Prompt file not found at {file_path}"


def get_prompt(agent_type: str, prompt_name: str) -> str:
    '''Public API to read prompt dynamically.'''
    return _read_prompt(agent_type, prompt_name)


# Legacy constants for compatibility (will be stale if files change after import)
INTENT_CLASSIFIER_PROMPT = _read_prompt("intent", "classifier")
INTENT_VALIDATOR_PROMPT = _read_prompt("intent", "validator")
MANAGER_TASK_DECOMPOSER_PROMPT = _read_prompt("managerial", "task_decomposer")
MANAGER_RESPONSE_AGGREGATOR_PROMPT = _read_prompt("managerial", "response_aggregator")
ACTION_GITHUB_PARSER_PROMPT = _read_prompt("action", "github_parser")
ACTION_CALENDAR_PARSER_PROMPT = _read_prompt("action", "calendar_parser")
ACTION_NOTION_PARSER_PROMPT = _read_prompt("action", "notion_parser")
ACTION_GMAIL_PARSER_PROMPT = _read_prompt("action", "gmail_parser")
