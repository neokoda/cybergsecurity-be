from datetime import datetime
from sqlalchemy.orm import Session
from models.workflow import Workflow, StatusEnum
from models.contract import Contract
from models.user import User

def seed_workflows(db: Session):
    contracts = db.query(Contract).all()
    users = db.query(User).all()
    
    workflows_data = [
        {
            "contract_id": contracts[0].id,
            "step": "Legal Review",
            "assigned_to": users[2].uuid,
            "status": StatusEnum.ON_REVIEW,
            "notes": "Reviewing legal compliance and terms",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "contract_id": contracts[0].id,
            "step": "Technical Verification",
            "assigned_to": users[3].uuid,
            "status": StatusEnum.NEW,
            "notes": "Pending legal review completion",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "contract_id": contracts[1].id,
            "step": "Budget Approval",
            "assigned_to": users[1].uuid,
            "status": StatusEnum.ON_VERIFICATION,
            "notes": "Verifying budget allocation",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "contract_id": contracts[1].id,
            "step": "Technical Specification Review",
            "assigned_to": users[3].uuid,
            "status": StatusEnum.ACCEPTED,
            "notes": "Technical specs approved",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "contract_id": contracts[2].id,
            "step": "Final Approval",
            "assigned_to": users[0].uuid,
            "status": StatusEnum.ACCEPTED,
            "notes": "Partnership agreement finalized",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "contract_id": contracts[3].id,
            "step": "Initial Review",
            "assigned_to": users[2].uuid,
            "status": StatusEnum.NEW,
            "notes": "Awaiting initial document review",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "contract_id": contracts[4].id,
            "step": "Conflict Resolution",
            "assigned_to": users[0].uuid,
            "status": StatusEnum.CONFLICT,
            "notes": "Resolving terms and conditions dispute",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]
    
    for workflow_data in workflows_data:
        workflow = Workflow(**workflow_data)
        db.add(workflow)
    
    db.commit()
    print("Workflows seeded successfully")