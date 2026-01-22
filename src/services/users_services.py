from sqlalchemy.orm import Session
from models.users_model import User
from schemas.users_schemas import UserCreate
from core.security import hash_password, verify_password
from sqlalchemy import or_

def authenticate_user(db: Session, login_id: str, password: str):
    user = db.query(User).filter(
        or_(User.email == login_id, User.name == login_id)
    ).first()
    
    if not user:
        return False
    
    if not verify_password(password, user.hashed_password):
        return False
        
    return user

def create_user_service(db: Session, user_data: UserCreate):
    db_user = User(
        name=user_data.name, 
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        role=user_data.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user