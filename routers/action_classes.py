from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status
from pydantic import UUID4
from models.session import Session
from models.session_reference import SessionReference as SessionReferenceModel
from models.comment import Comment as CommentModel
from models.contract_version import ContractVersion as ContractVersionModel
from models.contract import Contract as ContractModel
from schema.comments import CommentCreate, CommentUpdate
from schema.session_reference import SessionReferenceCreate

class CommentCRUD:
    @staticmethod
    def get_comment(db: Session, comment_id: int) -> Optional[CommentModel]:
        return db.query(CommentModel).filter(CommentModel.id == comment_id).first()
    
    @staticmethod
    def get_comments(db: Session, skip: int = 0, limit: int = 100) -> List[CommentModel]:
        return db.query(CommentModel).order_by(CommentModel.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_comments_by_session(db: Session, session_id: int, skip: int = 0, limit: int = 100) -> List[CommentModel]:
        return db.query(CommentModel).filter(CommentModel.session_id == session_id).order_by(CommentModel.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_comments_by_user(db: Session, user_id: UUID4, skip: int = 0, limit: int = 100) -> List[CommentModel]:
        return db.query(CommentModel).filter(CommentModel.user_id == user_id).order_by(CommentModel.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_comment(db: Session, comment: CommentCreate, current_user) -> CommentModel:
        db_comment = CommentModel(
            session_id=comment.session_id,
            user_id=current_user.uuid,
            comment=comment.comment,
            created_at=datetime.now()
        )
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        return db_comment
    
    @staticmethod
    def update_comment(db: Session, comment_id: int, comment_update: CommentUpdate, current_user) -> Optional[CommentModel]:
        db_comment = db.query(CommentModel).filter(CommentModel.id == comment_id).first()
        if not db_comment:
            return None
        
        # Check if user owns the comment
        if db_comment.user_id != current_user.uuid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this comment"
            )
        
        update_data = comment_update.dict(exclude_unset=True)
        if update_data:
            for field, value in update_data.items():
                setattr(db_comment, field, value)
            
            db.commit()
            db.refresh(db_comment)
        return db_comment
    
class SessionReferenceCRUD:
    @staticmethod
    def get_session_reference(db: Session, session_reference_id: int) -> Optional[SessionReferenceModel]:
        return db.query(SessionReferenceModel).filter(SessionReferenceModel.id == session_reference_id).first()
    
    @staticmethod
    def get_session_references(db: Session, skip: int = 0, limit: int = 100) -> List[SessionReferenceModel]:
        return db.query(SessionReferenceModel).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_session_references_by_session(db: Session, session_id: int, skip: int = 0, limit: int = 100) -> List[SessionReferenceModel]:
        return db.query(SessionReferenceModel).filter(SessionReferenceModel.session_id == session_id).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_session_references_by_validator(db: Session, validated_by: UUID4, skip: int = 0, limit: int = 100) -> List[SessionReferenceModel]:
        return db.query(SessionReferenceModel).filter(SessionReferenceModel.validated_by == validated_by).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_session_reference(db: Session, session_reference: SessionReferenceCreate, current_user) -> SessionReferenceModel:
        db_session_reference = SessionReferenceModel(
            session_id=session_reference.session_id,
            reference_id=session_reference.reference_id,
            notes=session_reference.notes,
            validated_by=session_reference.validated_by,
            validated_at=datetime.now()
        )
        db.add(db_session_reference)
        db.commit()
        db.refresh(db_session_reference)
        return db_session_reference

class ContractVersionCRUD:
    @staticmethod
    def get_latest_version_number(db: Session, contract_id: int, session_id: int) -> int:
        latest_version = db.query(ContractVersionModel)\
            .join(ContractModel)\
            .filter(ContractModel.id == contract_id)\
            .filter(ContractVersionModel.session_id == session_id)\
            .order_by(ContractVersionModel.version_number.desc())\
            .first()
        
        return latest_version.version_number if latest_version else 0
    
    @staticmethod
    def create_contract_version(
        db: Session, 
        contract_id: int, 
        session_id: int, 
        file_path: str, 
        current_user
    ) -> ContractVersionModel:
        latest_version = ContractVersionCRUD.get_latest_version_number(db, contract_id, session_id)
        new_version_number = latest_version + 1
        
        db_contract_version = ContractVersionModel(
            session_id=session_id,
            file_path=file_path,
            version_number=new_version_number,
            uploaded_by=current_user.uuid,
            created_at=datetime.utcnow()
        )
        
        db.add(db_contract_version)
        db.commit()
        db.refresh(db_contract_version)
        return db_contract_version
    
    @staticmethod
    def get_contract_versions(db: Session, contract_id: int, session_id: int):
        return db.query(ContractVersionModel)\
            .join(ContractModel)\
            .filter(ContractModel.id == contract_id)\
            .filter(ContractVersionModel.session_id == session_id)\
            .order_by(ContractVersionModel.version_number.desc())\
            .all()

class ContractUploadCRUD:
    @staticmethod
    def get_contract(db: Session, contract_id: int) -> Optional[ContractModel]:
        return db.query(ContractModel).filter(ContractModel.id == contract_id).first()
    
    @staticmethod
    def update_contract_file_path(db: Session, contract_id: int, file_path: str) -> Optional[ContractModel]:
        db_contract = db.query(ContractModel).filter(ContractModel.id == contract_id).first()
        if not db_contract:
            return None
        
        db_contract.file_path = file_path
        db_contract.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_contract)
        return db_contract