import json
import uuid
import re
import logging

# Mock logging and uuid for standalone test
class MockLogger:
    def info(self, msg): print(f"INFO: {msg}")
    def error(self, msg): print(f"ERROR: {msg}")

logger = MockLogger()

def test_normalization(tasks_json):
    print(f"\n--- Testing JSON ---\n{tasks_json}")
    try:
        tasks_data = json.loads(tasks_json)
        
        # Handle wrapped format: {"tasks": [...], "execution_order": [...]}
        if isinstance(tasks_data, dict) and "tasks" in tasks_data:
            logger.info("Detected wrapped JSON format from LLM")
            tasks_data = tasks_data["tasks"]
            
        if not isinstance(tasks_data, list):
            # If it's a single dict, wrap it in a list
            if isinstance(tasks_data, dict):
                tasks_data = [tasks_data]
            else:
                raise ValueError(f"Expected list of tasks from LLM, got {type(tasks_data).__name__}")
        
        # Assign a UUID to each task, but preserve the original ID for dependency resolution
        for i, task in enumerate(tasks_data):
            orig_id = task.get("task_id")
            task["original_task_id"] = str(orig_id) if orig_id is not None else None
            
            # Normalize arguments/parameters
            if "arguments" not in task and "parameters" in task:
                task["arguments"] = task["parameters"]
            if "arguments" not in task:
                task["arguments"] = {}
            
            # Ensure step is an integer and present
            if "step" not in task:
                if orig_id is not None:
                    try:
                        # Try to extract number from "task_1" or "1"
                        nums = re.findall(r'\d+', str(orig_id))
                        if nums:
                            task["step"] = int(nums[0])
                        else:
                            task["step"] = i + 1
                    except (ValueError, TypeError):
                        task["step"] = i + 1
                else:
                    task["step"] = i + 1
            else:
                try:
                    task["step"] = int(task["step"])
                except (ValueError, TypeError):
                    task["step"] = i + 1
            
            task["task_id"] = str(uuid.uuid4())
            
        print("Normalized Tasks:")
        for t in tasks_data:
            print(f"  Step {t.get('step')}: {t.get('description')} (Orig ID: {t.get('original_task_id')})")
            if "step" not in t:
                print("  !!! MISSING STEP !!!")
        
        return tasks_data
    except Exception as e:
        print(f"Error during normalization: {e}")
        return None

# Test Cases

# 1. Standard list
test_1 = """
[
  {
    "task_id": "task_1",
    "step": 1,
    "description": "Task 1",
    "parameters": {"a": 1}
  }
]
"""

# 2. Wrapped object
test_2 = """
{
  "tasks": [
    {
      "task_id": "task_1",
      "step": 1,
      "description": "Task 1",
      "parameters": {"a": 1}
    }
  ],
  "execution_order": ["task_1"]
}
"""

# 3. Missing step, string task_id
test_3 = """
[
  {
    "task_id": "task_1",
    "description": "Task 1 with string ID",
    "parameters": {"a": 1}
  }
]
"""

# 4. Missing step, missing task_id
test_4 = """
[
  {
    "description": "Task with nothing",
    "parameters": {"a": 1}
  }
]
"""

# 5. Parameters instead of arguments
test_5 = """
[
  {
    "task_id": 1,
    "step": 1,
    "description": "Task 1",
    "parameters": {"param": "val"}
  }
]
"""

test_normalization(test_1)
test_normalization(test_2)
test_normalization(test_3)
test_normalization(test_4)
test_normalization(test_5)
