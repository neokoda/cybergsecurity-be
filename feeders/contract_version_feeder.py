from datetime import datetime
from sqlalchemy.orm import Session
from models.contract_version import ContractVersion
from models.contract import Contract
from models.user import User

def seed_contract_versions(db: Session):
    contracts = db.query(Contract).all()
    users = db.query(User).all()
    
    versions_data = []
    
    for i, contract in enumerate(contracts):
        versions_data.append({
            "session_id": None,
            "file_path": f"/documents/contracts/contract_{contract.id}_v1.pdf",
            "version_number": 1,
            "uploaded_by": users[i % len(users)].uuid,
            "created_at": datetime.now()
        })
        
        if i < 2:
            versions_data.append({
                "session_id": None,
                "file_path": f"/documents/contracts/contract_{contract.id}_v2.pdf",
                "version_number": 2,
                "uploaded_by": users[(i + 1) % len(users)].uuid,
                "created_at": datetime.now()
            })
    
    for version_data in versions_data:
        version = ContractVersion(**version_data)
        db.add(version)
    
    db.commit()
    print("Contract versions seeded successfully")