import os
from typing import List
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from pydantic import UUID4
from schema.contract_version import ContractVersion
from routers.action_classes import CommentCRUD, ContractUploadCRUD, ContractVersionCRUD, SessionReferenceCRUD
from schema.comments import Comment, CommentCreate, CommentUpdate
from utils.auth import JWTBearerWithRole
from utils.db import get_db
from schema.session_reference import SessionReference, SessionReferenceCreate
from models.contract_version import ContractVersion as ContractVersionModel
from models.contract import Contract as ContractModel

router = APIRouter(prefix="/api/actions", tags=["actions"])

@router.post("/session-reference", response_model=SessionReference, status_code=status.HTTP_201_CREATED)
def create_session_reference(
    session_reference: SessionReferenceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(JWTBearerWithRole(roles=["manager", "reviewer"]))
):
    return SessionReferenceCRUD.create_session_reference(
        db=db, session_reference=session_reference, current_user=current_user
    )

@router.get("/session-reference", response_model=List[SessionReference])
def get_session_references(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(JWTBearerWithRole(roles=["user", "manager", "reviewer"]))
):
    session_references = SessionReferenceCRUD.get_session_references(db=db, skip=skip, limit=limit)
    return session_references

@router.get("/session-reference/{session_reference_id}", response_model=SessionReference)
def get_session_reference(
    session_reference_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(JWTBearerWithRole(roles=["user", "manager", "reviewer"]))
):
    db_session_reference = SessionReferenceCRUD.get_session_reference(db=db, session_reference_id=session_reference_id)
    if db_session_reference is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session reference not found"
        )
    return db_session_reference

@router.get("/session-reference/session/{session_id}", response_model=List[SessionReference])
def get_session_references_by_session(
    session_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(JWTBearerWithRole(roles=["user", "manager", "reviewer"]))
):
    session_references = SessionReferenceCRUD.get_session_references_by_session(
        db=db, session_id=session_id, skip=skip, limit=limit
    )
    return session_references

@router.get("/session-reference/{session_reference_id}/exists", response_model=dict)
def check_session_reference_exists(
    session_reference_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(JWTBearerWithRole(roles=["user", "manager", "reviewer"]))
):
    exists = SessionReferenceCRUD.get_session_reference(db=db, session_reference_id=session_reference_id) is not None
    return {"exists": exists}

@router.post("comments/", response_model=Comment, status_code=status.HTTP_201_CREATED)
def create_comment(
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(JWTBearerWithRole(roles=["user", "manager", "reviewer"]))
):
    return CommentCRUD.create_comment(db=db, comment=comment, current_user=current_user)

@router.get("comments/", response_model=List[Comment])
def get_comments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(JWTBearerWithRole(roles=["user", "manager", "reviewer"]))
):
    comments = CommentCRUD.get_comments(db=db, skip=skip, limit=limit)
    return comments

@router.get("comments/{comment_id}", response_model=Comment)
def get_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(JWTBearerWithRole(roles=["user", "manager", "reviewer"]))
):
    db_comment = CommentCRUD.get_comment(db=db, comment_id=comment_id)
    if db_comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    return db_comment

@router.get("comments/session/{session_id}", response_model=List[Comment])
def get_comments_by_session(
    session_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(JWTBearerWithRole(roles=["user", "manager", "reviewer"]))
):

    comments = CommentCRUD.get_comments_by_session(
        db=db, session_id=session_id, skip=skip, limit=limit
    )
    return comments

@router.get("/user/{user_id}", response_model=List[Comment])
def get_comments_by_user(
    user_id: UUID4,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(JWTBearerWithRole(roles=["manager", "reviewer"]))  # Only managers/reviewers can view user's comments
):
    """Get all comments by a specific user, ordered by creation date (newest first)."""
    comments = CommentCRUD.get_comments_by_user(
        db=db, user_id=user_id, skip=skip, limit=limit
    )
    return comments

@router.put("/{comment_id}", response_model=Comment)
def update_comment(
    comment_id: int,
    comment_update: CommentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(JWTBearerWithRole(roles=["manager", "reviewer"]))
):
    db_comment = CommentCRUD.update_comment(
        db=db, comment_id=comment_id, comment_update=comment_update, current_user=current_user
    )
    if db_comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    return db_comment

# Helper function to save uploaded file
async def save_uploaded_file(file: UploadFile, contract_id: int, version_number: int) -> str:
    """Save uploaded file and return the file path"""
    # Create directory if it doesn't exist
    upload_dir = f"uploads/contracts/{contract_id}"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate file name with version
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
    filename = f"contract_v{version_number}.{file_extension}" if file_extension else f"contract_v{version_number}"
    file_path = os.path.join(upload_dir, filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    return file_path

@router.post("/{contract_id}/upload", response_model=dict, status_code=status.HTTP_201_CREATED)
async def upload_contract_file(
    contract_id: int,
    session_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(JWTBearerWithRole(roles=["user", "manager"]))
):    
    db_contract = ContractUploadCRUD.get_contract(db=db, contract_id=contract_id)
    if not db_contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file selected"
        )
    
    next_version = ContractVersionCRUD.get_latest_version_number(db, contract_id, session_id) + 1
    
    try:
        file_path = await save_uploaded_file(file, contract_id, next_version)
        
        contract_version = ContractVersionCRUD.create_contract_version(
            db=db,
            contract_id=contract_id,
            session_id=session_id,
            file_path=file_path,
            current_user=current_user
        )
        
        updated_contract = ContractUploadCRUD.update_contract_file_path(
            db=db,
            contract_id=contract_id,
            file_path=file_path
        )
        
        return {
            "message": "Contract file uploaded successfully",
            "contract_id": contract_id,
            "session_id": session_id,
            "version_number": contract_version.version_number,
            "file_path": file_path,
            "uploaded_by": str(current_user.uuid),
            "uploaded_at": contract_version.created_at
        }
        
    except Exception as e:
        # Clean up file if database operations failed
        try:
            if 'file_path' in locals():
                os.remove(file_path)
        except:
            pass
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )

@router.get("/{contract_id}/versions", response_model=0)
def get_contract_versions(
    contract_id: int,
    session_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(JWTBearerWithRole(roles=["user", "manager", "reviewer"]))
):
    db_contract = ContractUploadCRUD.get_contract(db=db, contract_id=contract_id)
    if not db_contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    
    versions = ContractVersionCRUD.get_contract_versions(db, contract_id, session_id)
    return versions

@router.get("/{contract_id}/versions/latest", response_model=ContractVersion)
def get_latest_contract_version(
    contract_id: int,
    session_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(JWTBearerWithRole(roles=["user", "manager", "reviewer"]))
):
    """Get the latest version of a contract for a specific session"""
    
    # Check if contract exists
    db_contract = ContractUploadCRUD.get_contract(db=db, contract_id=contract_id)
    if not db_contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    
    latest_version = db.query(ContractVersionModel)\
        .join(ContractModel)\
        .filter(ContractModel.id == contract_id)\
        .filter(ContractVersionModel.session_id == session_id)\
        .order_by(ContractVersionModel.version_number.desc())\
        .first()
    
    if not latest_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No versions found for this contract in the specified session"
        )
    
    return latest_version

@router.get("/{contract_id}/versions/count", response_model=dict)
def get_contract_versions_count(
    contract_id: int,
    session_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(JWTBearerWithRole(roles=["user", "manager", "reviewer"]))
):
    db_contract = ContractUploadCRUD.get_contract(db=db, contract_id=contract_id)
    if not db_contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    
    count = db.query(ContractVersionModel)\
        .join(ContractModel)\
        .filter(ContractModel.id == contract_id)\
        .filter(ContractVersionModel.session_id == session_id)\
        .count()
    
    return {"contract_id": contract_id, "session_id": session_id, "version_count": count}