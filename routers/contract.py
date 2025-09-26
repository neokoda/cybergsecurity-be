from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import UUID4

from utils.auth import JWTBearerWithRole
from utils.db import get_db
from models.contract import Contract as ContractModel
from schema.contract import Contract, ContractCreate, ContractUpdate

router = APIRouter(prefix="/contracts", tags=["contracts"])

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
    def create_contract(db: Session, contract: ContractCreate, current_user) -> ContractModel:
        db_contract = ContractModel(
            title=contract.title,
            description=contract.description,
            jenis_kontrak=contract.jenis_kontrak,
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
    contract: ContractCreate,
    db: Session = Depends(get_db),
    current_user=Depends(JWTBearerWithRole(roles=["user"]))
):
    return ContractCRUD.create_contract(db=db, contract=contract, current_user=current_user)

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
            status_code=status.HTTP_404_NOT_FOUND,
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
