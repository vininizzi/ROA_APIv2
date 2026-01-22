from sqlalchemy.orm import Session
from models.users_model import User
from schemas.users_schemas import UserCreate
from core.security import hash_password

def create_user_service(db: Session, user_data: UserCreate):
    db_user = User(
        name=user_data.name, 
        email=user_data.email,
        hashed_password=hash_password(user_data.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user