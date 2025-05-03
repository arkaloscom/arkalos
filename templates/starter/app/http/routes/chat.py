
from dataclasses import dataclass
from fastapi import Form, Depends
from arkalos import router
from arkalos.ai import DWHAgent



@dataclass
class ChatRequest:
    message: str = Form(...)

@router.post("/chat")
async def chat(request: ChatRequest = Depends()):
    agent = DWHAgent()
    return await agent.handleHttp(request.message)



@router.get("/chat-intro")
async def chat():
    agent = DWHAgent()
    return agent.GREETING


