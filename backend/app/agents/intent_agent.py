from langgraph.graph import StateGraph, END
from typing import Dict, Any
import json
import re

from app.agents.state import AgentState
from app.core.openrouter import OpenRouterClient
from app.core.prompts import INTENT_CLASSIFIER_PROMPT, INTENT_VALIDATOR_PROMPT

class IntentAgent:
    """
    Intent Agent: Classifies and validates user input.
    """
    
    def __init__(self, openrouter_client: OpenRouterClient):
        self.openrouter = openrouter_client
    
    async def classify_intent(self, state: AgentState) -> AgentState:
        """
        Classify user input into structured intent.
        """
        user_input = state["user_input"]
        
        # Prepare prompt with context
        prompt = INTENT_CLASSIFIER_PROMPT.replace("{{current_date}}", "2026-04-21")
        
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
        json_match = re.search(r'```json\\n(.*?)\\n```', content, re.DOTALL)
        if json_match:
            content = json_match.group(1)
        
        try:
            intent_data = json.loads(content)
            state["validated_intent"] = intent_data
            state["intent_confidence"] = intent_data.get("confidence", 0.5)
            # Set the threshold for clarification
            state["needs_clarification"] = intent_data.get("confidence", 1.0) < 0.8 
        except (json.JSONDecodeError, AttributeError):
            # Handle cases where the model returns invalid JSON or no confidence
            state["validated_intent"] = {}
            state["intent_confidence"] = 0.0
            state["needs_clarification"] = True
        
        return state
    
    async def validate_intent(self, state: AgentState) -> AgentState:
        """
        If confidence is low, use the validator prompt to generate a clarifying question.
        """
        if not state.get("needs_clarification"):
            return state
        
        user_input = state["user_input"]
        
        # Prepare prompt for the validator
        prompt = INTENT_VALIDATOR_PROMPT

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
        json_match = re.search(r'```json\\n(.*?)\\n```', content, re.DOTALL)
        if json_match:
            content = json_match.group(1)
        
        try:
            validation_data = json.loads(content)
            question = validation_data.get("clarification_question", "I'm sorry, I don't understand. Could you please rephrase?")
            state["clarification_question"] = question
        except (json.JSONDecodeError, AttributeError):
            state["clarification_question"] = "I'm sorry, I'm having trouble understanding. Could you explain in a different way?"
            
        return state

def create_intent_node(openrouter_client: OpenRouterClient):
    """Create Intent Agent node for LangGraph."""
    agent = IntentAgent(openrouter_client)
    
    async def intent_node(state: AgentState) -> AgentState:
        state = await agent.classify_intent(state)
        state = await agent.validate_intent(state)
        return state
    
    return intent_node
