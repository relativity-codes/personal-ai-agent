from app.db.repositories.user_repository import UserRepository
import json

from app.agents.state import AgentState
from app.core.openrouter import OpenRouterClient
from app.core.prompts import MANAGER_RESPONSE_AGGREGATOR_PROMPT
from app.db.repositories.audit_repository import AuditRepository
import logging
from app.utils.logger import log_exception

logger = logging.getLogger(__name__)

class ResponseAgent:
    """
    Response Agent: Aggregates results and generates the final user-facing response.
    """
    
    def __init__(self, openrouter_client: OpenRouterClient, user_repo: UserRepository, audit_repo: AuditRepository):
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
            context = "\n".join(json.dumps(result) for result in raw_results)
            
            # Add user context to the prompt
            user_info = ""
            user_context = state.get("user_context", {})
            if user_context:
                info_parts = [f"{k}: {v}" for k, v in user_context.items() if v]
                user_info = "\nUser Profile Information:\n" + "\n".join(info_parts) + "\n\n"

            system_prompt = (
                MANAGER_RESPONSE_AGGREGATOR_PROMPT
                + user_info
                + "\n\n---\n## Current run: tool results (JSON)\n"
                + context
            )

            response = await self.openrouter.complete(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f'Original query: {state["user_input"]}'},
                ],
                temperature=0.7,
                max_tokens=1500,
            )

            final_response = response["choices"][0]["message"]["content"]
            print("_________\n\n\nIntent agent response", final_response);
            state["final_response"] = final_response

            return state
        except Exception as e:
            log_exception(logger, e, context=f"Failed to generate response for session {state.get('session_id')}")
            state["error"] = str(e)
            return state

def create_response_node(openrouter_client: OpenRouterClient, user_repo: UserRepository, audit_repo: AuditRepository):
    """Create Response Agent node for LangGraph."""
    agent = ResponseAgent(openrouter_client, user_repo, audit_repo)

    async def response_node(state: AgentState) -> AgentState:
        return await agent.generate_response(state)

    return response_node
