from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models.comment import Comment
from models.session import Session as SessionModel
from models.user import User

def seed_comments(db: Session):
    sessions = db.query(SessionModel).all()
    users = db.query(User).all()
    
    comments_data = [
        {
            "session_id": sessions[0].id,
            "user_id": users[2].uuid,
            "comment": "Klausul keamanan data perlu diperkuat sesuai standar ISO 27001",
            "created_at": datetime.now() - timedelta(days=2)
        },
        {
            "session_id": sessions[0].id,
            "user_id": users[1].uuid,
            "comment": "Setuju dengan review keamanan, namun timeline perlu disesuaikan",
            "created_at": datetime.now() - timedelta(days=1)
        },
        {
            "session_id": sessions[0].id,
            "user_id": users[0].uuid,
            "comment": "Approved untuk revisi keamanan, silakan lanjutkan ke versi berikutnya",
            "created_at": datetime.now()
        },
        {
            "session_id": sessions[1].id,
            "user_id": users[3].uuid,
            "comment": "Spesifikasi teknis server sudah sesuai requirement",
            "created_at": datetime.now() - timedelta(hours=5)
        },
        {
            "session_id": sessions[1].id,
            "user_id": users[1].uuid,
            "comment": "Budget allocation telah diverifikasi dan approved",
            "created_at": datetime.now() - timedelta(hours=2)
        },
        {
            "session_id": sessions[2].id,
            "user_id": users[0].uuid,
            "comment": "Partnership agreement telah final dan siap untuk implementasi",
            "created_at": datetime.now() - timedelta(days=3)
        },
        {
            "session_id": sessions[4].id,
            "user_id": users[2].uuid,
            "comment": "Terdapat konflik pada klausul liability, perlu diskusi lebih lanjut",
            "created_at": datetime.now() - timedelta(hours=8)
        },
        {
            "session_id": sessions[4].id,
            "user_id": users[1].uuid,
            "comment": "Suggested resolution: modify liability cap to 50% of contract value",
            "created_at": datetime.now() - timedelta(hours=3)
        }
    ]
    
    for comment_data in comments_data:
        comment = Comment(**comment_data)
        db.add(comment)
    
    db.commit()
    print("Comments seeded successfully")