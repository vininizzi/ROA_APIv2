from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str
    
class UserRead(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool

    class Config:
        orm_mode = True
        from_attributes = True