from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from utils.auth import JWTBearerWithRole
from utils.db import get_db
from models.session import Session as SessionModel
from schema.session import Session, SessionCreate, SessionUpdate

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])

class SessionCRUD:
    @staticmethod
    def get_session(db: DBSession, session_id: int) -> Optional[SessionModel]:
        return db.query(SessionModel).filter(SessionModel.id == session_id).first()
    
    @staticmethod
    def get_sessions(db: DBSession, skip: int = 0, limit: int = 100) -> List[SessionModel]:
        return db.query(SessionModel).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_sessions_by_contract(db: DBSession, contract_id: int, skip: int = 0, limit: int = 100) -> List[SessionModel]:
        return db.query(SessionModel).filter(SessionModel.contract_id == contract_id).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_session(db: DBSession, session: SessionCreate, current_user) -> SessionModel:
        db_session = SessionModel(
            contract_id=session.contract_id,
            current_version_id=session.current_version_id,
            summary=session.summary,
            due_date=session.due_date,
            risk_status=session.risk_status,
            status=session.status,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        return db_session
    
    @staticmethod
    def update_session(db: DBSession, session_id: int, session_update: SessionUpdate) -> Optional[SessionModel]:
        db_session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if not db_session:
            return None
        
        update_data = session_update.dict(exclude_unset=True)
        if update_data:
            update_data['updated_at'] = datetime.utcnow()
            for field, value in update_data.items():
                setattr(db_session, field, value)
            
            db.commit()
            db.refresh(db_session)
        return db_session
    
    @staticmethod
    def delete_session(db: DBSession, session_id: int) -> bool:
        db_session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if not db_session:
            return False
        
        db.delete(db_session)
        db.commit()
        return True

@router.post("/", response_model=Session, status_code=status.HTTP_201_CREATED)
def create_session(
    session: SessionCreate,
    db: DBSession = Depends(get_db),
    current_user=Depends(JWTBearerWithRole(roles=["user"]))
):
    return SessionCRUD.create_session(db=db, session=session, current_user=current_user)

@router.get("/", response_model=List[Session])
def get_sessions(
    skip: int = 0,
    limit: int = 100,
    db: DBSession = Depends(get_db),
    current_user=Depends(JWTBearerWithRole(roles=["user", "manager", "reviewer"]))
):
    sessions = SessionCRUD.get_sessions(db=db, skip=skip, limit=limit)
    return sessions

@router.get("/{session_id}", response_model=Session)
def get_session(
    session_id: int,
    db: DBSession = Depends(get_db),
    current_user=Depends(JWTBearerWithRole(roles=["user", "manager", "reviewer"]))
):
    db_session = SessionCRUD.get_session(db=db, session_id=session_id)
    if db_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return db_session

@router.get("/contract/{contract_id}", response_model=List[Session])
def get_sessions_by_contract(
    contract_id: int,
    skip: int = 0,
    limit: int = 100,
    db: DBSession = Depends(get_db),
    current_user=Depends(JWTBearerWithRole(roles=["user", "manager", "reviewer"]))
):
    sessions = SessionCRUD.get_sessions_by_contract(
        db=db, contract_id=contract_id, skip=skip, limit=limit
    )
    return sessions

@router.put("/{session_id}", response_model=Session)
def update_session(
    session_id: int,
    session_update: SessionUpdate,
    db: DBSession = Depends(get_db),
    current_user=Depends(JWTBearerWithRole(roles=["user"]))
):
    db_session = SessionCRUD.update_session(
        db=db, session_id=session_id, session_update=session_update
    )
    if db_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return db_session

@router.patch("/{session_id}", response_model=Session)
def partial_update_session(
    session_id: int,
    session_update: SessionUpdate,
    db: DBSession = Depends(get_db),
    current_user=Depends(JWTBearerWithRole(roles=["user"]))
):
    db_session = SessionCRUD.update_session(
        db=db, session_id=session_id, session_update=session_update
    )
    if db_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return db_session

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: int,
    db: DBSession = Depends(get_db),
    current_user=Depends(JWTBearerWithRole(roles=["user"]))
):
    success = SessionCRUD.delete_session(db=db, session_id=session_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return None

@router.get("/{session_id}/exists", response_model=dict)
def check_session_exists(
    session_id: int,
    db: DBSession = Depends(get_db),
    current_user=Depends(JWTBearerWithRole(roles=["user", "manager", "reviewer"]))
):
    exists = SessionCRUD.get_session(db=db, session_id=session_id) is not None
    return {"exists": exists}

@router.get("/contract/{contract_id}/count", response_model=dict)
def get_sessions_count_by_contract(
    contract_id: int,
    db: DBSession = Depends(get_db),
    current_user=Depends(JWTBearerWithRole(roles=["user", "manager", "reviewer"]))
):
    count = db.query(SessionModel).filter(SessionModel.contract_id == contract_id).count()
    return {"count": count}