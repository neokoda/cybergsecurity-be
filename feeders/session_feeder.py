from datetime import datetime
from sqlalchemy.orm import Session
from models.session import Session as SessionModel
from models.contract import Contract
from models.contract_version import ContractVersion
from models.enums import StatusEnum, RiskStatusEnum

def seed_sessions(db: Session):
    contracts = db.query(Contract).all()
    versions = db.query(ContractVersion).all()
    
    sessions_data = [
        {
            "contract_id": contracts[0].id,
            "current_version_id": versions[1].id if len(versions) > 1 else versions[0].id,
            "summary": "Review kontrak sistem manajemen dokumen digital. Perlu revisi pada klausul keamanan data.",
            "risk_status": RiskStatusEnum.RISK,
            "status": StatusEnum.ON_REVIEW,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "contract_id": contracts[1].id,
            "current_version_id": versions[2].id if len(versions) > 2 else versions[0].id,
            "summary": "Kontrak pengadaan server dalam tahap verifikasi teknis.",
            "risk_status": RiskStatusEnum.COMPLY,
            "status": StatusEnum.ON_VERIFICATION,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "contract_id": contracts[2].id,
            "current_version_id": versions[3].id if len(versions) > 3 else versions[0].id,
            "summary": "Kemitraan strategis telah disetujui dan siap untuk implementasi.",
            "risk_status": RiskStatusEnum.COMPLY,
            "status": StatusEnum.ACCEPTED,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "contract_id": contracts[3].id,
            "current_version_id": versions[4].id if len(versions) > 4 else versions[0].id,
            "summary": "Kontrak integrasi logistik masih dalam review awal.",
            "risk_status": RiskStatusEnum.COMPLY,
            "status": StatusEnum.NEW,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "contract_id": contracts[4].id,
            "current_version_id": versions[5].id if len(versions) > 5 else versions[0].id,
            "summary": "Platform pelabuhan digital mengalami konflik pada terms and conditions.",
            "risk_status": RiskStatusEnum.RISK,
            "status": StatusEnum.CONFLICT,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]
    
    for session_data in sessions_data:
        session = SessionModel(**session_data)
        db.add(session)
    
    db.commit()
    print("Sessions seeded successfully")