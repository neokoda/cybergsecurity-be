from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import os
import json
import PyPDF2
import pdfplumber
import requests
from dotenv import load_dotenv
import vertexai.preview
from vertexai.preview import rag
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

router = APIRouter(prefix="/api/compliance", tags=["Compliance"])

class ComplianceRequest(BaseModel):
    file_url: str

class ComplianceResponse(BaseModel):
    status: str
    summary: str

def download_file_from_url(url: str) -> str:
    if "storage.googleapis.com" in url:
        try:
            return download_from_gcs(url)
        except:
            return download_with_requests(url)
    else:
        return download_with_requests(url)

def download_with_requests(url: str) -> str:
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail=f"Cannot download file: HTTP {response.status_code}")
    
    file_extension = ".pdf" if url.lower().endswith('.pdf') else ".txt"
    temp_filename = f"temp_{hash(url)}{file_extension}"
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
        
        file_extension = ".pdf" if url.lower().endswith('.pdf') else ".txt"
        temp_filename = f"temp_{hash(url)}{file_extension}"
        blob.download_to_filename(temp_filename)
        
        return temp_filename
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cannot download from GCS: {str(e)}")

def read_file_content(file_path: str) -> str:
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == '.pdf':
        content = ""
        
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        content += page_text + "\n"
                if content.strip():
                    print(f"DEBUG: pdfplumber success, length: {len(content)}")
                    return content
                else:
                    print("DEBUG: pdfplumber extracted empty content")
        except Exception as e:
            print(f"DEBUG: pdfplumber failed: {e}")
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                content = ""
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        content += page_text + "\n"
                if content.strip():
                    print(f"DEBUG: PyPDF2 success, length: {len(content)}")
                    return content
                else:
                    print("DEBUG: PyPDF2 extracted empty content")
        except Exception as e:
            print(f"DEBUG: PyPDF2 failed: {e}")
        
        return "Error: PDF tidak mengandung teks yang dapat diekstrak atau merupakan PDF berbasis gambar"
    else:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                if content.startswith('%PDF'):
                    return "Error: File PDF tidak dapat dibaca sebagai teks"
                return content
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    content = file.read()
                    if content.startswith('%PDF'):
                        return "Error: File PDF tidak dapat dibaca sebagai teks"
                    return content
            except Exception as e:
                return f"Error: Tidak dapat membaca file - {str(e)}"

def evaluate_file_compliance(file_content: str) -> dict:
    if len(file_content.strip()) < 50:
        return {
            "status": "error",
            "summary": "Konten dokumen terlalu sedikit atau tidak dapat diekstrak dengan benar"
        }
    
    if file_content.startswith("Error:"):
        return {
            "status": "error",
            "summary": file_content
        }
    
    prompt = f"""
    Cek apakah klausul dalam kontrak ini bertentangan dengan peraturan hukum Indonesia.
    
    KONTRAK:
    {file_content[:8000]}
    
    JSON response:
    {{
        "status": "comply" atau "risk",
        "summary": "Jelaskan klausul mana yang conflict dengan peraturan. Jika tidak ada conflict, tulis 'comply'"
    }}
    """
    
    try:
        print(f"DEBUG: project_id={project_id}, location={location}, corpus_name={corpus_name}")
        
        corpus_resource = f"projects/{project_id}/locations/{location}/ragCorpora/6917529027641081856"
        
        retrieval_tool = Tool.from_retrieval(
            retrieval=rag.Retrieval(
                source=rag.VertexRagStore(
                    rag_resources=[rag.RagResource(rag_corpus=corpus_resource)],
                    rag_retrieval_config=rag.RagRetrievalConfig(top_k=5),
                )
            )
        )
        
        model = GenerativeModel("gemini-2.5-pro", tools=[retrieval_tool])
        response = model.generate_content(prompt)
        
    except Exception as e:
        print(f"DEBUG: RAG error: {str(e)}")
        return {
            "status": "risk", 
            "summary": f"RAG connection failed: {str(e)}"
        }
    
    try:
        response_text = response.text.strip()
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        
        if start_idx != -1 and end_idx > start_idx:
            json_str = response_text[start_idx:end_idx]
            result = json.loads(json_str)
            return result
        else:
            return {"status": "risk", "summary": "Format response error"}
            
    except:
        return {"status": "risk", "summary": "Parsing error, review manual needed"}

@router.post("/evaluate", response_model=ComplianceResponse)
def evaluate_compliance(request: ComplianceRequest):
    temp_file = None
    
    try:
        temp_file = download_file_from_url(request.file_url)
        file_content = read_file_content(temp_file)
        
        print(f"DEBUG: File content length: {len(file_content)}")
        print(f"DEBUG: First 200 chars: {file_content[:200]}")
        
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
            try:
                os.remove(temp_file)
            except:
                pass
