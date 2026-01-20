from sqlalchemy.orm import Session
from models.users_model import User
from schemas.users_schemas import UserCreate

def create_user_service(db: Session, user_data: UserCreate):
    db_user = User(
        name=user_data.name, 
        email=user_data.email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user