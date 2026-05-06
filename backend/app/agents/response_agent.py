from typing import Any
from app.db.repositories.user_repository import UserRepository
import json

from app.agents.state import AgentState
from app.core.openrouter import OpenRouterClient
from app.core.prompts import MANAGER_RESPONSE_AGGREGATOR_PROMPT
from app.db.repositories.audit_repository import AuditRepository
import logging
from app.utils.logger import log_exception

from app.utils.serialization import make_serializable, safe_json_dumps

logger = logging.getLogger(__name__)

class ResponseAgent:
    """Aggregates results and generates the final user-facing response."""
    
    def __init__(self, openrouter_client: Any, user_repo: UserRepository, audit_repo: AuditRepository):
        self.openrouter = openrouter_client
        self.user_repo = user_repo
        self.audit_repo = audit_repo

    async def generate_response(self, state: AgentState) -> AgentState:
        try:
            if state.get("needs_clarification"):
                state["final_response"] = state.get("clarification_question")
                return state

            raw_results = state.get("results")
            if not raw_results:
                raw_results = list(state.get("task_results", {}).values())
            
            context = "\n".join(safe_json_dumps(result) for result in raw_results)
            
            user_info = ""
            user_context = state.get("user_context", {})
            if user_context:
                info_parts = [f"{k}: {v}" for k, v in user_context.items() if v]
                user_info = "\nUser Profile Information:\n" + "\n".join(info_parts) + "\n\n"

            intent_context = f"\n\nValidated Intent: {safe_json_dumps(state.get('validated_intent'))}"
            
            system_prompt = (
                MANAGER_RESPONSE_AGGREGATOR_PROMPT
                + user_info
                + intent_context
                + "\n\n---\n## Current run: tool results (JSON)\n"
                + context
            )

            if hasattr(self.openrouter, "ainvoke"):
                from langchain_core.messages import HumanMessage, SystemMessage
                resp = await self.openrouter.ainvoke([
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=f'Original query: {state["user_input"]}')
                ])
                final_response = resp.content
            else:
                response = await self.openrouter.complete(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f'Original query: {state["user_input"]}'},
                    ],
                    temperature=0.7,
                    max_tokens=1500,
                )
                final_response = response["choices"][0]["message"]["content"]

            if not final_response:
                 final_response = "I processed your request but could not generate a summary. Please try again."
            
            logger.info(f"Response agent generated final response for session {state.get('session_id')}")
            state["final_response"] = final_response
            return state

        except Exception as e:
            log_exception(logger, e, context=f"Failed to generate response for session {state.get('session_id')}")
            state["error"] = str(e)
            return state

def create_response_node(openrouter_client: Any, user_repo: UserRepository, audit_repo: AuditRepository):
    agent = ResponseAgent(openrouter_client, user_repo, audit_repo)

    async def response_node(state: AgentState) -> AgentState:
        return await agent.generate_response(state)

    return response_node
