from app.agents.state import AgentState
from app.core.openrouter import OpenRouterClient
from app.core.prompts import RESPONSE_AGGREGATOR_PROMPT
import json
from app.db.repositories.user_repository import UserRepository
from app.db.repositories.audit_repository import AuditRepository

class ResponseAgent:
    """
    Response Agent: Aggregates results and generates the final user-facing response.
    """
    
    def __init__(self, openrouter_client: OpenRouterClient, user_repo: UserRepository, audit_repo: AuditRepository):
        self.openrouter = openrouter_client
        self.user_repo = user_repo
        self.audit_repo = audit_repo

    async def generate_response(self, state: AgentState) -> AgentState:
        """
        Generates a final response based on the aggregated results or asks a clarifying question.
        """
        # If clarification is needed, the final response is the clarifying question.
        if state.get("needs_clarification"):
            state["final_response"] = state.get("clarification_question")
            return state

        # Otherwise, aggregate the results into a comprehensive response.
        context = "\n".join(json.dumps(result) for result in state.get("results", []))
        prompt = RESPONSE_AGGREGATOR_PROMPT.format(context=context)

        response = await self.openrouter.complete(
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f'Original query: {state["user_input"]}'}
            ],
            temperature=0.7,
            max_tokens=1500
        )

        final_response = response["choices"][0]["message"]["content"]
        state["final_response"] = final_response
        
        return state

def create_response_node(openrouter_client: OpenRouterClient, user_repo: UserRepository, audit_repo: AuditRepository):
    """Create Response Agent node for LangGraph."""
    agent = ResponseAgent(openrouter_client, user_repo, audit_repo)

    async def response_node(state: AgentState) -> AgentState:
        return await agent.generate_response(state)

    return response_node
