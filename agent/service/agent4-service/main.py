
# app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from .service import agent_service

from fastapi.responses import StreamingResponse
import json
import asyncio


app = FastAPI(
    title="Agentic RAG Agent4 Service",
    version="1.0.0",
    description="FastAPI microservice for agentic RAG with Phoenix instrumentation",
)


# --- Schemas ---
class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Unique session id for the conversation")
    user_input: str = Field(..., description="User message to the agent")

class ChatResponse(BaseModel):
    session_id: str
    answer: str
    history_length: int

class ResetRequest(BaseModel):
    session_id: str

class ResetResponse(BaseModel):
    session_id: str
    status: str

# --- Endpoints ---
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        answer = agent_service.chat(session_id=request.session_id, user_input=request.user_input)
        return ChatResponse(
            session_id=request.session_id,
            answer=answer,
            history_length=agent_service.history_length(request.session_id),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process chat: {str(e)}")

@app.post("/reset", response_model=ResetResponse)
def reset(req: ResetRequest):
    try:
        agent_service.reset(req.session_id)
        return ResetResponse(session_id=req.session_id, status="reset")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset: {str(e)}")




@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Streams partial tokens. This assumes your underlying agent can yield chunks.
    If not, you can simulate by chunking the final answer.
    """

    async def token_generator():
        try:
            # 1) Get the final answer from the usual call (blocking)
            #    Replace with your true streaming agent if available.
            answer = agent_service.chat(session_id=request.session_id, user_input=request.user_input)

            # 2) Simulate streaming by chunking the final answer
            for chunk in split_into_chunks(answer, size=40):
                yield json.dumps({"token": chunk}).encode("utf-8") + b"\n"
                await asyncio.sleep(0.02)

            # Signal end
            yield json.dumps({"event": "end"}).encode("utf-8") + b"\n"

        except Exception as e:
            yield json.dumps({"error": str(e)}).encode("utf-8") + b"\n"

    def split_into_chunks(text: str, size: int = 40):
        for i in range(0, len(text), size):
            yield text[i:i+size]

    return StreamingResponse(token_generator(), media_type="application/json")
