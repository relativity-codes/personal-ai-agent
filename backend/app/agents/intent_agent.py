from typing import Dict, Any
import json
import re
import logging

from app.agents.state import AgentState
from app.core.openrouter import OpenRouterClient
from app.core.prompts import INTENT_CLASSIFIER_PROMPT, INTENT_VALIDATOR_PROMPT
from app.db.repositories.user_repository import UserRepository
from app.db.repositories.audit_repository import AuditRepository
from app.utils.logger import log_exception

logger = logging.getLogger(__name__)


class IntentAgent:
    """
    Intent Agent:
    - Classifies user input into structured intent
    - Optionally triggers clarification if confidence is low
    """

    def __init__(
        self,
        openrouter_client: OpenRouterClient,
        user_repo: UserRepository,
        audit_repo: AuditRepository,
    ):
        self.openrouter = openrouter_client
        self.user_repo = user_repo
        self.audit_repo = audit_repo

    # ----------------------------
    # 1. INTENT CLASSIFICATION
    # ----------------------------
    async def classify_intent(self, state: AgentState) -> AgentState:
        user_input = state["user_input"]
        chat_history = state.get("chat_history") or []

        prompt = INTENT_CLASSIFIER_PROMPT.replace(
            "{{current_date}}", "2026-04-24"
        )

        user_context = state.get("user_context", {})
        if user_context:
            context_str = "\n".join(
                f"{k}: {v}" for k, v in user_context.items() if v
            )
            prompt += f"\n\nUser Context:\n{context_str}"

        formatted_history = "\n".join(
            f'{msg["role"]}: {msg["message"]}' for msg in chat_history
        )
        prompt += f"\n\nConversation History:\n{formatted_history}"

        try:
            response = await self.openrouter.complete(
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user_input},
                ],
                temperature=0.2,
                max_tokens=500,
            )

            content = response["choices"][0]["message"]["content"]

            # Extract JSON safely
            json_match = re.search(r"```(?:json)?\s*(.*?)\s*```", content, re.DOTALL)
            if json_match:
                content = json_match.group(1)
            else:
                obj_match = re.search(r"(\{.*\})", content, re.DOTALL)
                if obj_match:
                    content = obj_match.group(1)

            intent_data = json.loads(content)

            confidence = intent_data.get("confidence", 0.0)

            state["validated_intent"] = intent_data
            state["intent_confidence"] = confidence
            state["needs_clarification"] = confidence < 0.8

            return state

        except Exception as e:
            log_exception(
                logger,
                e,
                context=f"Intent classification failed: {user_input}",
            )

            state["validated_intent"] = {}
            state["intent_confidence"] = 0.0
            state["needs_clarification"] = True
            state["error"] = str(e)

            return state

    # ----------------------------
    # 2. CLARIFICATION GENERATION
    # ----------------------------
    async def validate_intent(self, state: AgentState) -> AgentState:
        if not state.get("needs_clarification"):
            return state

        try:
            response = await self.openrouter.complete(
                messages=[
                    {"role": "system", "content": INTENT_VALIDATOR_PROMPT},
                    {"role": "user", "content": state["user_input"]},
                ],
                temperature=0.2,
                max_tokens=150,
            )

            content = response["choices"][0]["message"]["content"]

            json_match = re.search(r"```(?:json)?\s*(.*?)\s*```", content, re.DOTALL)
            if json_match:
                content = json_match.group(1)
            else:
                obj_match = re.search(r"(\{.*\})", content, re.DOTALL)
                if obj_match:
                    content = obj_match.group(1)

            validation_data = json.loads(content)

            state["clarification_question"] = validation_data.get(
                "clarification_question",
                "Could you clarify your request?",
            )

            return state

        except Exception as e:
            log_exception(
                logger,
                e,
                context="Intent validation failed",
            )

            state["clarification_question"] = (
                "I’m having trouble understanding your request. Could you rephrase it?"
            )
            state["error"] = str(e)

            return state


# ----------------------------
# 3. SINGLE NODE ENTRYPOINT
# ----------------------------
def create_intent_node(
    openrouter_client: OpenRouterClient,
    user_repo: UserRepository,
    audit_repo: AuditRepository,
):
    agent = IntentAgent(openrouter_client, user_repo, audit_repo)

    async def intent_node(state: AgentState) -> AgentState:
        state = await agent.classify_intent(state)

        if state.get("needs_clarification"):
            state = await agent.validate_intent(state)

        return state

    return intent_node