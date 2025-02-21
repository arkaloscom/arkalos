from dataclasses import dataclass

from fastapi import WebSocket
from arkalos import router
from arkalos.ai import DWHAgent



@dataclass
class ChatRequest:
    message: str



@router.post("/chat")
async def chat(request: ChatRequest):
    agent = DWHAgent()
    return agent.handleHttp(request.message)



@router.websocket("/chat-socket")
async def chat_socket(websocket: WebSocket):
    agent = DWHAgent()
    await websocket.accept()
    await websocket.send_text(agent.GREETING) # Send greeting
    try:
        while True:
            message = await websocket.receive_text()
            
            async def send_response(text: str):
                await websocket.send_text(text)
            
            agent.handleWebSocket(message, send_response)
            
    except Exception as e:
        await websocket.send_text(f"Connection error: {str(e)}")