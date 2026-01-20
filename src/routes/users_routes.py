from schemas.users import UserCreate, UserRead
from models.users import User
from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

users_router = APIRouter(prefix="/users", tags=["users"])
@users_router.post("/", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user