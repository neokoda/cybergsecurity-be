from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import os
import json
import vertexai
from dotenv import load_dotenv
from vertexai.preview import rag
from vertexai.generative_models import GenerativeModel, Tool

load_dotenv()

project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
corpus_name = os.getenv("RAG_CORPUS")
credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

if credentials_path:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

vertexai.init(project=project_id, location=location)

router = APIRouter(prefix="/chatbot", tags=["chatbot"])

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    sources: list = []

def get_rag_response(user_message: str) -> dict:
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
        
        prompt = f"""
        Jawab pertanyaan berikut berdasarkan knowledge base yang tersedia.
        Berikan jawaban yang informatif dan akurat dalam bahasa Indonesia.
        
        Pertanyaan: {user_message}
        """
        
        response = model.generate_content(prompt)
        
        return {
            "response": response.text,
            "sources": []
        }
        
    except Exception as e:
        return {
            "response": f"Maaf, terjadi kesalahan saat memproses pertanyaan Anda: {str(e)}",
            "sources": []
        }

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Pesan tidak boleh kosong")
        
        result = get_rag_response(request.message)
        
        return ChatResponse(
            response=result["response"],
            sources=result["sources"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/health")
def health_check():
    return {"status": "healthy", "service": "RAG Chatbot"}