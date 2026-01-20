from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas.users_schemas import UserCreate, UserRead
from services.users_services import create_user_service

users_router = APIRouter(prefix="/users", tags=["users"])

@users_router.post("/", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return create_user_service(db=db, user_data=user)