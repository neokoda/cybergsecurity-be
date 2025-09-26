from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models.chat_log import ChatLog
from models.session import Session as SessionModel
from models.user import User

def seed_chat_logs(db: Session):
    sessions = db.query(SessionModel).all()
    users = db.query(User).all()
    
    chat_logs_data = [
        {
            "session_id": sessions[0].id,
            "user_id": users[0].uuid,
            "message": "Mulai review kontrak sistem manajemen dokumen",
            "created_at": datetime.now() - timedelta(days=5)
        },
        {
            "session_id": sessions[0].id,
            "user_id": users[2].uuid,
            "message": "Saya akan fokus pada aspek legal compliance",
            "created_at": datetime.now() - timedelta(days=5, hours=1)
        },
        {
            "session_id": sessions[0].id,
            "user_id": users[1].uuid,
            "message": "Timeline review diperkirakan 3 hari kerja",
            "created_at": datetime.now() - timedelta(days=4)
        },
        {
            "session_id": sessions[1].id,
            "user_id": users[1].uuid,
            "message": "Kontrak pengadaan server masuk tahap verifikasi budget",
            "created_at": datetime.now() - timedelta(days=3)
        },
        {
            "session_id": sessions[1].id,
            "user_id": users[3].uuid,
            "message": "Spesifikasi teknis sudah saya review dan approve",
            "created_at": datetime.now() - timedelta(days=2)
        },
        {
            "session_id": sessions[2].id,
            "user_id": users[0].uuid,
            "message": "Partnership agreement dengan regional partner sudah final",
            "created_at": datetime.now() - timedelta(days=7)
        },
        {
            "session_id": sessions[4].id,
            "user_id": users[1].uuid,
            "message": "Ada issue di terms and conditions yang perlu diselesaikan",
            "created_at": datetime.now() - timedelta(hours=12)
        },
        {
            "session_id": sessions[4].id,
            "user_id": users[2].uuid,
            "message": "Saya akan coordinate dengan legal team untuk resolution",
            "created_at": datetime.now() - timedelta(hours=10)
        },
        {
            "session_id": sessions[4].id,
            "user_id": users[0].uuid,
            "message": "Please prioritize this conflict resolution",
            "created_at": datetime.now() - timedelta(hours=8)
        },
        {
            "session_id": sessions[3].id,
            "user_id": users[2].uuid,
            "message": "Kontrak logistik akan saya review minggu ini",
            "created_at": datetime.now() - timedelta(hours=6)
        }
    ]
    
    for chat_data in chat_logs_data:
        chat_log = ChatLog(**chat_data)
        db.add(chat_log)
    
    db.commit()
    print("Chat logs seeded successfully")