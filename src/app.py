import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import get_db
from routes import general_routes, users_routes, ROA_routes
from ROA.vectorstore_manager import load_vectorstore
import logging
from ROA.vectorstore_manager import load_vectorstore
from services.ROA_services import delete_document_service

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)

logger = logging.getLogger("ROA")


app = FastAPI(title="sql alchemy")

@app.on_event("startup")
def startup_event():
    load_vectorstore()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(general_routes.general_router)
app.include_router(users_routes.users_router)
app.include_router(ROA_routes.ROA_router)

if __name__ == "__main__":
    uvicorn.run("app:app", reload=True)