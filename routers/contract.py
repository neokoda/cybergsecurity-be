from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import UUID4

from utils.auth import JWTBearerWithRole
from utils.db import get_db
from utils.gcs_storage import upload_file_to_gcs
from models.contract import Contract as ContractModel
from schema.contract import Contract, ContractCreate, ContractUpdate

router = APIRouter(prefix="/api/contracts", tags=["contracts"])

class ContractCRUD:
    @staticmethod
    def get_contract(db: Session, contract_id: int) -> Optional[ContractModel]:
        return db.query(ContractModel).filter(ContractModel.id == contract_id).first()
    
    @staticmethod
    def get_contracts(db: Session, skip: int = 0, limit: int = 100) -> List[ContractModel]:
        return db.query(ContractModel).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_contracts_by_creator(db: Session, creator_id: UUID4, skip: int = 0, limit: int = 100) -> List[ContractModel]:
        return db.query(ContractModel).filter(ContractModel.created_by == creator_id).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_contract(db: Session, contract_data: ContractCreate, file_path: str, current_user) -> ContractModel:
        db_contract = ContractModel(
            title=contract_data.title,
            description=contract_data.description,
            jenis_kontrak=contract_data.jenis_kontrak,
            file_path=file_path,
            created_by=current_user.uuid,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(db_contract)
        db.commit()
        db.refresh(db_contract)
        return db_contract
    
    @staticmethod
    def update_contract(db: Session, contract_id: int, contract_update: ContractUpdate) -> Optional[ContractModel]:
        db_contract = db.query(ContractModel).filter(ContractModel.id == contract_id).first()
        if not db_contract:
            return None
        
        update_data = contract_update.dict(exclude_unset=True)
        
        if update_data:
            update_data['updated_at'] = datetime.utcnow()
            for field, value in update_data.items():
                setattr(db_contract, field, value)
            
            db.commit()
            db.refresh(db_contract)
        return db_contract
    
    @staticmethod
    def delete_contract(db: Session, contract_id: int) -> bool:
        db_contract = db.query(ContractModel).filter(ContractModel.id == contract_id).first()
        if not db_contract:
            return False
        
        db.delete(db_contract)
        db.commit()
        return True

@router.post("/", response_model=Contract, status_code=status.HTTP_201_CREATED)
def create_contract(
    title: str = Form(...),
    description: str = Form(...),
    jenis_kontrak: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(JWTBearerWithRole(roles=["user"]))
):
    
    file_path = upload_file_to_gcs(file, title)
    
    contract_data = ContractCreate(
        title=title,
        description=description,
        jenis_kontrak=jenis_kontrak,
        file_path=file_path
    )
    
    return ContractCRUD.create_contract(
        db=db, 
        contract_data=contract_data, 
        file_path=file_path,
        current_user=current_user
    )

@router.get("/", response_model=List[Contract])
def get_contracts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(JWTBearerWithRole(roles=["user", "manager", "reviewer"]))
):
    contracts = ContractCRUD.get_contracts(db=db, skip=skip, limit=limit)
    return contracts

@router.get("/{contract_id}", response_model=Contract)
def get_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(JWTBearerWithRole(roles=["user", "manager", "reviewer"]))
):
    db_contract = ContractCRUD.get_contract(db=db, contract_id=contract_id)
    if db_contract is None:
        raise HTTPException(
            status_code=status.HTTP_400_NOT_FOUND,
            detail="Contract not found"
        )
    return db_contract

@router.get("/creator/{creator_id}", response_model=List[Contract])
def get_contracts_by_creator(
    creator_id: UUID4,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(JWTBearerWithRole(roles=["user", "manager", "reviewer"]))
):
    contracts = ContractCRUD.get_contracts_by_creator(
        db=db, creator_id=creator_id, skip=skip, limit=limit
    )
    return contracts

@router.put("/{contract_id}", response_model=Contract)
def update_contract(
    contract_id: int,
    contract_update: ContractUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(JWTBearerWithRole(roles=["user"]))
):
    db_contract = ContractCRUD.update_contract(
        db=db, contract_id=contract_id, contract_update=contract_update
    )
    if db_contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    return db_contract

@router.patch("/{contract_id}", response_model=Contract)
def partial_update_contract(
    contract_id: int,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    jenis_kontrak: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user=Depends(JWTBearerWithRole(roles=["user"]))
):
    db_contract_existing = ContractCRUD.get_contract(db=db, contract_id=contract_id)
    if not db_contract_existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
        
    new_file_path = None
    if file and file.filename:
        upload_title = title if title is not None else db_contract_existing.title
        new_file_path = upload_file_to_gcs(file, upload_title)
        
    update_data = {}
    if title is not None:
        update_data["title"] = title
    if description is not None:
        update_data["description"] = description
    if jenis_kontrak is not None:
        update_data["jenis_kontrak"] = jenis_kontrak
    
    if new_file_path:
        update_data["file_path"] = new_file_path
        
    contract_update = ContractUpdate(**update_data)
    
    db_contract = ContractCRUD.update_contract(
        db=db, 
        contract_id=contract_id, 
        contract_update=contract_update
    )
    
    if db_contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    return db_contract

@router.delete("/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(JWTBearerWithRole(roles=["user"]))
):
    success = ContractCRUD.delete_contract(db=db, contract_id=contract_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    return None

@router.get("/{contract_id}/exists", response_model=dict)
def check_contract_exists(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(JWTBearerWithRole(roles=["user", "manager", "reviewer"]))
):
    exists = ContractCRUD.get_contract(db=db, contract_id=contract_id) is not None
    return {"exists": exists}

@router.get("/creator/{creator_id}/count", response_model=dict)
def get_contracts_count_by_creator(
    creator_id: UUID4,
    db: Session = Depends(get_db),
    current_user=Depends(JWTBearerWithRole(roles=["user", "manager", "reviewer"]))
):
    count = db.query(ContractModel).filter(ContractModel.created_by == creator_id).count()
    return {"count": count}