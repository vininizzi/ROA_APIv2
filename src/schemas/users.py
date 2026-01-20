from pydantic import BaseModel

class CreateUserSchema(BaseModel):
    name: str
    email: str
    
class UserResponseSchema(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool

    class Config:
        orm_mode = True
        from_attributes = True