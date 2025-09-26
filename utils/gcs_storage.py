from datetime import datetime
from fastapi import HTTPException, status, UploadFile
from google.cloud import storage
from google.cloud.storage.blob import Blob

GCS_BUCKET_NAME = "cybergsecurity"
GCS_CLIENT = storage.Client()

def upload_file_to_gcs(file: UploadFile, contract_title: str) -> str:
    try:
        bucket = GCS_CLIENT.bucket(GCS_BUCKET_NAME)
        
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        safe_title = contract_title.replace(" ", "_").replace("/", "_").strip()
        
        file_extension = file.filename.split('.')[-1] if file.filename and '.' in file.filename else 'dat'
        gcs_filename = f"contracts/{safe_title}_{timestamp}.{file_extension}"
        
        blob = bucket.blob(gcs_filename)
        
        blob.upload_from_file(file.file, content_type=file.content_type)

        return f"gs://{GCS_BUCKET_NAME}/{gcs_filename}"
    
    except Exception as e:
        print(f"GCS Upload Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload contract file to storage."
        )
    
def get_gcs_blob_for_download(gcs_path: str) -> Blob:
    if not gcs_path or not gcs_path.startswith("gs://"):
        raise HTTPException(status_code=400, detail="Invalid GCS file path.")
        
    try:
        parts = gcs_path[len("gs://"):].split("/", 1)
        bucket_name = parts[0]
        blob_name = parts[1]
    except IndexError:
        raise HTTPException(status_code=400, detail="Invalid GCS path structure.")

    try:
        bucket = GCS_CLIENT.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        
        if not blob.exists():
            raise HTTPException(status_code=404, detail="Contract file not found in storage.")
            
        return blob
    except Exception as e:
        print(f"GCS Access Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to access storage.")