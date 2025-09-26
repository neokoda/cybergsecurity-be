from datetime import datetime
from sqlalchemy.orm import Session
from models.session_reference import SessionReference
from models.session import Session as SessionModel
from models.document_reference import DocumentReference
from models.user import User

def seed_session_references(db: Session):
    sessions = db.query(SessionModel).all()
    references = db.query(DocumentReference).all()
    users = db.query(User).all()
    
    session_refs_data = [
        {
            "session_id": sessions[0].id,
            "reference_id": references[0].id,
            "notes": "Security standards must be applied for document management system",
            "validated_by": users[2].uuid,
            "validated_at": datetime.now()
        },
        {
            "session_id": sessions[0].id,
            "reference_id": references[5].id,
            "notes": "Data privacy policy compliance required",
            "validated_by": users[2].uuid,
            "validated_at": datetime.now()
        },
        {
            "session_id": sessions[1].id,
            "reference_id": references[1].id,
            "notes": "Using standard procurement template",
            "validated_by": users[1].uuid,
            "validated_at": datetime.now()
        },
        {
            "session_id": sessions[2].id,
            "reference_id": references[2].id,
            "notes": "Partnership guidelines successfully applied",
            "validated_by": users[0].uuid,
            "validated_at": datetime.now()
        },
        {
            "session_id": sessions[3].id,
            "reference_id": references[3].id,
            "notes": "Logistics regulation review pending",
            "validated_by": users[3].uuid,
            "validated_at": datetime.now()
        },
        {
            "session_id": sessions[4].id,
            "reference_id": references[4].id,
            "notes": "Digital port standards need clarification",
            "validated_by": users[1].uuid,
            "validated_at": datetime.now()
        }
    ]
    
    for ref_data in session_refs_data:
        session_ref = SessionReference(**ref_data)
        db.add(session_ref)
    
    db.commit()
    print("Session references seeded successfully")