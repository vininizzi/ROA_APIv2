from database import SessionLocal
from models.users_model import User
db = SessionLocal()
print("Users:", [u.id for u in db.query(User).all()])
