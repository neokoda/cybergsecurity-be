from datetime import datetime
from fastapi import HTTPException, status, UploadFile
from google.cloud import storage

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