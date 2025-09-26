from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import os
import json
import vertexai
import PyPDF2
import requests
from dotenv import load_dotenv
from vertexai import rag
from vertexai.generative_models import GenerativeModel, Tool
from google.cloud import storage
import urllib.parse

load_dotenv()

project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
corpus_name = os.getenv("RAG_CORPUS")
credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

if credentials_path:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

vertexai.init(project=project_id, location=location)

router = APIRouter(
    prefix="/compliance",
    tags=["compliance"]
)

class ComplianceRequest(BaseModel):
    file_url: str

class ComplianceResponse(BaseModel):
    status: str
    summary: str

def download_file_from_url(url: str) -> str:
    if "storage.googleapis.com" in url:
        return download_from_gcs(url)
    else:
        response = requests.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Cannot download file from URL")
        
        temp_filename = f"temp_{hash(url)}.tmp"
        with open(temp_filename, 'wb') as f:
            f.write(response.content)
        
        return temp_filename

def download_from_gcs(url: str) -> str:
    try:
        parsed = urllib.parse.urlparse(url)
        path_parts = parsed.path.strip('/').split('/')
        bucket_name = path_parts[0]
        blob_name = '/'.join(path_parts[1:])
        blob_name = urllib.parse.unquote(blob_name)
        
        if credentials_path and os.path.exists(credentials_path):
            client = storage.Client.from_service_account_json(credentials_path)
        else:
            client = storage.Client(project=project_id)
        
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        
        temp_filename = f"temp_{hash(url)}.tmp"
        blob.download_to_filename(temp_filename)
        
        return temp_filename
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cannot download from GCS: {str(e)}")

def read_file_content(file_path: str) -> str:
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == '.pdf':
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            content = ""
            for page in pdf_reader.pages:
                content += page.extract_text() + "\n"
            return content
    else:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()

def evaluate_file_compliance(file_content: str) -> dict:
    prompt = f"""
    Evaluasi dokumen berikut terhadap pasal-pasal yang ada dalam database:
    
    DOKUMEN:
    {file_content}
    
    Berikan respons dalam format JSON berikut:
    {{
        "status": "risk" atau "comply",
        "summary": "ringkasan 1-2 paragraf tentang dokumen dan compliance terhadap pasal-pasal"
    }}
    
    Status "risk" jika ada potensi konflik dengan pasal-pasal yang ada.
    Status "comply" jika dokumen sudah sesuai dengan pasal-pasal yang berlaku.
    """
    
    rag_retrieval_config = rag.RagRetrievalConfig(
        top_k=10,
        filter=rag.Filter(vector_distance_threshold=0.3),
    )
    
    rag_retrieval_tool = Tool.from_retrieval(
        retrieval=rag.Retrieval(
            source=rag.VertexRagStore(
                rag_resources=[
                    rag.RagResource(rag_corpus=corpus_name)
                ],
                rag_retrieval_config=rag_retrieval_config,
            ),
        )
    )
    
    rag_model = GenerativeModel(
        model_name="gemini-2.5-flash", 
        tools=[rag_retrieval_tool]
    )
    
    response = rag_model.generate_content(prompt)
    
    try:
        response_text = response.text.strip()
        
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        elif response_text.startswith("```"):
            response_text = response_text.replace("```", "").strip()
        
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        
        if start_idx != -1 and end_idx != 0:
            json_str = response_text[start_idx:end_idx]
            result = json.loads(json_str)
            return result
        else:
            return {
                "status": "error",
                "summary": f"Format respons tidak valid"
            }
            
    except json.JSONDecodeError:
        return {
            "status": "error", 
            "summary": "Gagal memproses respons dari model"
        }

@router.post("/evaluate", response_model=ComplianceResponse)
def evaluate_compliance(request: ComplianceRequest):
    temp_file = None
    
    try:
        temp_file = download_file_from_url(request.file_url)
        file_content = read_file_content(temp_file)
        
        if not file_content.strip():
            raise HTTPException(status_code=400, detail="File content is empty")
        
        result = evaluate_file_compliance(file_content)
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["summary"])
        
        return ComplianceResponse(
            status=result["status"],
            summary=result["summary"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    finally:
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)