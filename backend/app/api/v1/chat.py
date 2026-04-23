from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Awaitable

from app.api.deps import get_current_user
from app.agents.managerial_agent import create_managerial_graph
from app.agents.state import AgentState
from langgraph.graph import StateGraph

# Define the request and response models for the chat endpoint
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

# Create the API router
router = APIRouter()

# --- Dependency Injection for the Graph ---
# By using a dependency injection system, we ensure that the graph is created
# only once and can be shared across multiple requests.

def get_managerial_graph():
    """Dependency to create and return the managerial agent graph."""
    graph = create_managerial_graph()
    return graph

# --- API Endpoint ---
@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user: dict = Depends(get_current_user),
    graph: StateGraph = Depends(get_managerial_graph),
) -> ChatResponse:
    """
    Main chat endpoint to handle user messages and orchestrate the agentic workflow.
    """
    session_id = user.get("user_id") # Or any other unique session identifier
    
    # 1. Initialize the AgentState
    # This is the starting point for our agentic workflow. The state will be
    # passed between the nodes of the graph, accumulating data as it goes.
    initial_state: AgentState = {
        "user_input": request.message,
        "session_id": session_id,
        "results": [],
        "tasks": [],
        "needs_clarification": False,
    }
    
    try:
        # 2. Invoke the Agentic Workflow
        # We run the graph asynchronously to avoid blocking the main thread.
        # The graph will execute the defined flow: intent -> task_planner -> action -> ...
        final_state = await graph.ainvoke(initial_state)

        # 3. Extract and Return the Final Response
        # The final response is either a clarifying question or the aggregated answer.
        response_message = final_state.get("final_response", "Sorry, I encountered an issue.")
        
        return ChatResponse(response=response_message)
        
    except Exception as e:
        # In case of any error during the graph execution, we return a generic error message.
        # In a production environment, you would want to log this error.
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
