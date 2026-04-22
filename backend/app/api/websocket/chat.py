from fastapi import APIRouter, WebSocket

router = APIRouter()


@router.websocket("/chat")
async def chat_socket(websocket: WebSocket):
    await websocket.accept()
    await websocket.close(code=1000)
