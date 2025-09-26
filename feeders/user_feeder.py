import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from models.user import User

def seed_users(db: Session):
    users_data = [
        {
            "uuid": uuid.uuid4(),
            "name": "John Doe",
            "email": "john.doe@company.com",
            "password": "hashed_password_1",
            "role": "admin",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "uuid": uuid.uuid4(),
            "name": "Jane Smith",
            "email": "jane.smith@company.com",
            "password": "hashed_password_2",
            "role": "manager",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "uuid": uuid.uuid4(),
            "name": "Bob Wilson",
            "email": "bob.wilson@company.com",
            "password": "hashed_password_3",
            "role": "reviewer",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "uuid": uuid.uuid4(),
            "name": "Alice Brown",
            "email": "alice.brown@company.com",
            "password": "hashed_password_4",
            "role": "user",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "uuid": uuid.uuid4(),
            "name": "Charlie Davis",
            "email": "charlie.davis@company.com",
            "password": "hashed_password_5",
            "role": "user",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]
    
    for user_data in users_data:
        user = User(**user_data)
        db.add(user)
    
    db.commit()
    print("Users seeded successfully")