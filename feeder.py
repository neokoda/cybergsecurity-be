from sqlalchemy.orm import sessionmaker
from config.db import engine
from feeders.user_feeder import seed_users
from feeders.document_reference_feeder import seed_document_references
from feeders.contract_feeder import seed_contracts
from feeders.contract_version_feeder import seed_contract_versions
from feeders.session_feeder import seed_sessions
from feeders.workflow_feeder import seed_workflows
from feeders.session_reference_feeder import seed_session_references
from feeders.comment_feeder import seed_comments
from feeders.chat_log_feeder import seed_chat_logs

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def run_all_feeders():
    db = SessionLocal()
    try:
        print("Starting database seeding...")
        
        seed_users(db)
        seed_document_references(db)
        seed_contracts(db)
        seed_contract_versions(db)
        seed_sessions(db)
        update_contract_versions_with_sessions(db)
        seed_workflows(db)
        seed_session_references(db)
        seed_comments(db)
        seed_chat_logs(db)
        
        print("All seeders completed successfully!")
        
    except Exception as e:
        print(f"Error during seeding: {str(e)}")
        db.rollback()
    finally:
        db.close()

def update_contract_versions_with_sessions(db):
    from models.contract_version import ContractVersion
    from models.session import Session as SessionModel
    
    sessions = db.query(SessionModel).all()
    versions = db.query(ContractVersion).all()
    
    for i, session in enumerate(sessions):
        if i < len(versions):
            versions[i].session_id = session.id
    
    db.commit()
    print("Contract versions updated with session IDs")

if __name__ == "__main__":
    run_all_feeders()