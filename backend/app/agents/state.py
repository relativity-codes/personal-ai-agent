from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    user_id: str
    session_id: str
    user_input: str
    validated_intent: dict[str, Any] | None
    final_response: str | None
