
from langgraph.graph import StateGraph, END
from typing import Dict, Any
import json
import re
import logging
from app.utils.logger import log_exception

logger = logging.getLogger(__name__)

from app.agents.state import AgentState
from app.core.openrouter import OpenRouterClient
from app.core.prompts import INTENT_CLASSIFIER_PROMPT, INTENT_VALIDATOR_PROMPT
from app.db.repositories.user_repository import UserRepository
from app.db.repositories.audit_repository import AuditRepository

class IntentAgent:
    """
    Intent Agent: Classifies and validates user input.
    """

    def __init__(self, openrouter_client: OpenRouterClient, user_repo: UserRepository, audit_repo: AuditRepository):
        self.openrouter = openrouter_client
        self.user_repo = user_repo
        self.audit_repo = audit_repo

    async def classify_intent(self, state: AgentState) -> AgentState:
        """
        Classify user input into structured intent.
        """
        user_input = state["user_input"]
        chat_history = state.get("chat_history") or []

        # Prepare prompt with context
        prompt = INTENT_CLASSIFIER_PROMPT.replace("{{current_date}}", "2026-04-24")
        
        # Add user context to the prompt
        user_context = state.get("user_context", {})
        if user_context:
            context_str = "\n".join([f"{k}: {v}" for k, v in user_context.items() if v])
            prompt = f"{prompt}\n\nUser Context:\n{context_str}"

        # Format chat history for the prompt
        formatted_history = "\n".join([f'{msg["role"]}: {msg["message"]}' for msg in chat_history])
        prompt = f'{prompt}\n\nConversation History:\n{formatted_history}'

        try:
            response = await self.openrouter.complete(
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.2,
                max_tokens=500
            )

            content = response["choices"][0]["message"]["content"]

            # Extract JSON
            json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)
            else:
                # Fallback: try to find anything that looks like a JSON object
                obj_match = re.search(r'(\{.*\})', content, re.DOTALL)
                if obj_match:
                    content = obj_match.group(1)

            try:
                intent_data = json.loads(content)
                state["validated_intent"] = intent_data
                state["intent_confidence"] = intent_data.get("confidence", 0.5)
                # Set the threshold for clarification
                state["needs_clarification"] = intent_data.get("confidence", 1.0) < 0.8
            except (json.JSONDecodeError, AttributeError) as e:
                logger.warning(f"Failed to parse intent JSON. Error: {e}. Content: {content}")
                # Handle cases where the model returns invalid JSON or no confidence
                state["validated_intent"] = {}
                state["intent_confidence"] = 0.0
                state["needs_clarification"] = True

            return state
        except Exception as e:
            log_exception(logger, e, context=f"Failed to classify intent for input: {user_input}")
            state["error"] = str(e)
            raise e

    async def validate_intent(self, state: AgentState) -> AgentState:
        """
        If confidence is low, use the validator prompt to generate a clarifying question.
        """
        if not state.get("needs_clarification"):
            return state

        user_input = state["user_input"]

        # Prepare prompt for the validator
        prompt = INTENT_VALIDATOR_PROMPT

        try:
            response = await self.openrouter.complete(
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.2,
                max_tokens=150
            )

            content = response["choices"][0]["message"]["content"]

            # The validator prompt is expected to return a JSON object with a "clarification_question" key.
            json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)
            else:
                obj_match = re.search(r'(\{.*\})', content, re.DOTALL)
                if obj_match:
                    content = obj_match.group(1)

            try:
                validation_data = json.loads(content)
                question = validation_data.get("clarification_question", "I'm sorry, I don't understand. Could you please rephrase?")
                state["clarification_question"] = question
            except (json.JSONDecodeError, AttributeError) as e:
                logger.warning(f"Failed to parse validation JSON. Error: {e}. Content: {content}")
                state["clarification_question"] = "I'm sorry, I'm having trouble understanding. Could you explain in a different way?"

            return state
        except Exception as e:
            log_exception(logger, e, context=f"Failed to validate intent for input: {user_input}")
            state["error"] = str(e)
            raise e

def create_intent_node(openrouter_client: OpenRouterClient, user_repo: UserRepository, audit_repo: AuditRepository):
    """Creates the intent agent node."""
    intent_agent = IntentAgent(openrouter_client, user_repo, audit_repo)

    async def intent_node(state: AgentState) -> AgentState:
        state = await intent_agent.classify_intent(state)
        if state.get("needs_clarification"):
            state = await intent_agent.validate_intent(state)
        return state

    return intent_node

def create_intent_workflow(openrouter_client: OpenRouterClient, user_repo: UserRepository, audit_repo: AuditRepository) -> StateGraph:
    """Creates the intent workflow."""
    intent_agent = IntentAgent(openrouter_client, user_repo, audit_repo)

    workflow = StateGraph(AgentState)
    workflow.add_node("classify_intent", intent_agent.classify_intent)
    workflow.add_node("validate_intent", intent_agent.validate_intent)

    workflow.set_entry_point("classify_intent")

    workflow.add_conditional_edges(
        "classify_intent",
        lambda state: "validate_intent" if state.get("needs_clarification") else END,
    )
    workflow.add_edge("validate_intent", END)

    return workflow.compile()
