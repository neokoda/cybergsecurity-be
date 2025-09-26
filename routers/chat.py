from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import os
import vertexai
from dotenv import load_dotenv
from vertexai.generative_models import GenerativeModel, Tool, Content, Part
import redis
import json
from vertexai.preview import rag
import asyncio

load_dotenv()

project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

vertexai.init(project=project_id, location=location)

router = APIRouter(prefix="/chatbot", tags=["chatbot"])

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

class ChatRequest(BaseModel):
    session_id: str
    message: str

class SummarizeRequest(BaseModel):
    session_id: str
    query: str

class ChatResponse(BaseModel):
    response: str
    sources: list = []

def get_history(session_id: str):
    key = f"chat:{session_id}"
    history = r.get(key)
    return json.loads(history) if history else []

def save_history(session_id: str, history: list):
    key = f"chat:{session_id}"
    r.set(key, json.dumps(history), ex=3600)

async def stream_chat_response(session_id: str, user_message: str):
    msg_lower = user_message.lower().strip()
    if msg_lower in ["tes", "halo", "hai", "anjay"]:
        short_reply = f"Halo 👋 maksud dari **{user_message}** apa ya?"
        yield short_reply.encode("utf-8")
        return
    if "udah chat apa aja" in msg_lower or "riwayat" in msg_lower:
        history = get_history(session_id)
        if not history:
            yield b"Belum ada chat sebelumnya."
            return
        chats = [f"{h['role']}: {h['content']}" for h in history]
        reply = "Riwayat percakapan kamu:\n" + "\n".join(chats)
        yield reply.encode("utf-8")
        return
    corpus_resource = f"projects/{project_id}/locations/{location}/ragCorpora/6917529027641081856"
    retrieval_tool = Tool.from_retrieval(
        retrieval=rag.Retrieval(
            source=rag.VertexRagStore(
                rag_resources=[rag.RagResource(rag_corpus=corpus_resource)],
            )
        )
    )
    model = GenerativeModel("gemini-2.5-flash", tools=[retrieval_tool])
    history = get_history(session_id)
    messages = []
    for h in history[-6:]:
        role = "user" if h["role"] == "user" else "model"
        messages.append(Content(role=role, parts=[Part.from_text(h["content"])]))
    messages.append(Content(role="user", parts=[Part.from_text(user_message)]))
    response = model.generate_content(messages, stream=True)
    history.append({"role": "user", "content": user_message})
    final_text = ""
    for chunk in response:
        if chunk.candidates and chunk.candidates[0].content.parts:
            text = chunk.candidates[0].content.parts[0].text
            if text:
                final_text += text
                yield text.encode("utf-8")
                await asyncio.sleep(0)
    if not final_text.strip():
        final_text = "Maaf, belum ada jawaban yang relevan."
    history.append({"role": "assistant", "content": final_text})
    if len(history) > 20:
        history = history[-20:]
    save_history(session_id, history)

def rag_response(session_id: str, query: str) -> dict:
    try:
        corpus_resource = f"projects/{project_id}/locations/{location}/ragCorpora/6917529027641081856"
        retrieval_tool = Tool.from_retrieval(
            retrieval=rag.Retrieval(
                source=rag.VertexRagStore(
                    rag_resources=[rag.RagResource(rag_corpus=corpus_resource)],
                )
            )
        )
        model = GenerativeModel("gemini-2.5-flash", tools=[retrieval_tool])
        prompt = f"Ringkas kontrak ini sesuai konteks hukum Indonesia: {query}"
        response = model.generate_content(prompt)
        return {"response": response.text, "sources": []}
    except Exception as e:
        return {"response": f"Error: {str(e)}", "sources": []}

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Pesan tidak boleh kosong")
    return StreamingResponse(stream_chat_response(request.session_id, request.message), media_type="text/plain")

@router.post("/summarize", response_model=ChatResponse)
def summarize(request: SummarizeRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query tidak boleh kosong")
    result = rag_response(request.session_id, request.query)
    return ChatResponse(response=result["response"], sources=result["sources"])

@router.get("/health")
def health_check():
    return {"status": "healthy", "service": "RAG Chatbot"}
