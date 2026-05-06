from typing import Literal, Dict, Any, List
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.state import AgentState
from app.agents.intent_agent import create_intent_node
from app.agents.response_agent import create_response_node
from app.agents.tools import get_mcp_tools
from app.core.config import settings
from app.db.repositories.user_repository import UserRepository
from app.db.repositories.audit_repository import AuditRepository

def create_managerial_graph() -> StateGraph:
    """Refactored orchestration graph using LangGraph's ReAct agent."""
    
    llm = ChatOpenAI(
        model=settings.OPENROUTER_DEFAULT_MODEL,
        openai_api_key=settings.OPENROUTER_API_KEY,
        openai_api_base=settings.OPENROUTER_BASE_URL,
        temperature=0.2,
        default_headers={
            "HTTP-Referer": settings.HOST,
            "X-Title": settings.APP_NAME,
        }
    )

    user_repo = UserRepository()
    audit_repo = AuditRepository()

    intent_node = create_intent_node(llm, user_repo, audit_repo)
    response_node = create_response_node(llm, user_repo, audit_repo)

    async def react_agent_node(state: AgentState) -> AgentState:
        """Executes the dynamic ReAct loop for tool calling."""
        user_id = state.get("user_id")
        tools = await get_mcp_tools(user_id)
        
        from app.core.prompts import get_prompt
        from datetime import datetime
        system_prompt = get_prompt("managerial", "react_agent").replace(
            "{{current_date}}", datetime.now().strftime("%Y-%m-%d")
        )
        
        agent = create_react_agent(llm, tools, prompt=system_prompt)
        input_messages = [HumanMessage(content=state["user_input"])]
        
        result = await agent.ainvoke({"messages": input_messages})
        
        from langchain_core.messages import ToolMessage
        import json
        tool_results = []
        for msg in result["messages"]:
            if isinstance(msg, ToolMessage):
                try:
                    tool_results.append(json.loads(msg.content))
                except:
                    tool_results.append(msg.content)
        
        state["results"] = tool_results
        return state

    workflow = StateGraph(AgentState)
    workflow.add_node("intent", intent_node)
    workflow.add_node("react_agent", react_agent_node)
    workflow.add_node("response", response_node)
    workflow.set_entry_point("intent")

    def route_from_intent(state: AgentState):
        intent = state.get("validated_intent") or {}
        return "react_agent" if intent else "response"

    workflow.add_conditional_edges(
        "intent",
        route_from_intent,
        {
            "react_agent": "react_agent",
            "response": "response",
        },
    )

    workflow.add_edge("react_agent", "response")
    workflow.add_edge("response", END)

    return workflow.compile()