from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import vertexai
from dotenv import load_dotenv
from vertexai import rag
from vertexai.generative_models import GenerativeModel, Tool, Content, Part
import redis
import json

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

def chat_response(session_id: str, user_message: str) -> dict:
    try:
        corpus_resource = f"projects/{project_id}/locations/{location}/ragCorpora/6917529027641081856"
        retrieval_tool = Tool.from_retrieval(
            retrieval=rag.Retrieval(
                source=rag.VertexRagStore(
                    rag_resources=[rag.RagResource(rag_corpus=corpus_resource)],
                    rag_retrieval_config=rag.RagRetrievalConfig(top_k=3),
                )
            )
        )
        model = GenerativeModel("gemini-2.5-flash", tools=[retrieval_tool])
        history = get_history(session_id)
        
        messages = []
        messages.append(Content(role="user", parts=[Part.from_text("Kamu adalah chatbot yang ramah dan natural. Jawab pertanyaan dengan santai seperti teman ngobrol. Gunakan RAG hanya untuk memvalidasi informasi hukum jika diperlukan, tapi jangan langsung kasih informasi berlebihan.")]))
        messages.append(Content(role="model", parts=[Part.from_text("Baik! Saya siap ngobrol dengan santai.")]))
        
        for h in history[-6:]:
            role = "user" if h["role"] == "user" else "model"
            messages.append(Content(role=role, parts=[Part.from_text(h["content"])]))
        
        messages.append(Content(role="user", parts=[Part.from_text(user_message)]))

        response = model.generate_content(messages)

        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": response.text})
        
        if len(history) > 20:
            history = history[-20:]
        
        save_history(session_id, history)

        return {"response": response.text, "sources": []}
    except Exception as e:
        return {"response": f"Error: {str(e)}", "sources": []}

def rag_response(session_id: str, query: str) -> dict:
    try:
        corpus_resource = f"projects/{project_id}/locations/{location}/ragCorpora/6917529027641081856"
        retrieval_tool = Tool.from_retrieval(
            retrieval=rag.Retrieval(
                source=rag.VertexRagStore(
                    rag_resources=[rag.RagResource(rag_corpus=corpus_resource)],
                    rag_retrieval_config=rag.RagRetrievalConfig(top_k=5),
                )
            )
        )
        model = GenerativeModel("gemini-2.5-flash", tools=[retrieval_tool])

        prompt = f"Berdasarkan dokumen hukum yang tersedia, jelaskan tentang: {query}"
        response = model.generate_content(prompt)

        return {"response": response.text, "sources": []}
    except Exception as e:
        return {"response": f"Error: {str(e)}", "sources": []}

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Pesan tidak boleh kosong")
    result = chat_response(request.session_id, request.message)
    return ChatResponse(response=result["response"], sources=result["sources"])

@router.post("/summarize", response_model=ChatResponse)
def summarize(request: SummarizeRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query tidak boleh kosong")
    result = rag_response(request.session_id, request.query)
    return ChatResponse(response=result["response"], sources=result["sources"])

@router.get("/health")
def health_check():
    return {"status": "healthy", "service": "RAG Chatbot"}