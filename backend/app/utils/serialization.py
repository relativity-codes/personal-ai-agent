import json
from typing import Any

def make_serializable(obj: Any) -> Any:
    """
    Recursively converts non-serializable objects (like MCP TextContent, 
    UUIDs, etc.) into JSON-serializable types (dicts, lists, strings).
    """
    if isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [make_serializable(i) for i in obj]
    elif hasattr(obj, 'dict') and callable(obj.dict):
        return make_serializable(obj.dict())
    elif hasattr(obj, '__dict__'):
        # For MCP TextContent and similar objects
        return {k: make_serializable(v) for k, v in obj.__dict__.items() if not k.startswith('_')}
    elif hasattr(obj, 'isoformat'): # Dates
        return obj.isoformat()
    elif isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    else:
        return str(obj)

def safe_json_dumps(obj: Any, **kwargs) -> str:
    """Dumps an object to JSON string, ensuring all parts are serializable."""
    return json.dumps(make_serializable(obj), **kwargs)
