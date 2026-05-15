from fastapi import FastAPI

from app.models.base import Base
from app.db import engine

from app.models.user_model import User
from app.models.item_model import Item
from app.models.interaction_model import Interaction




app = FastAPI(
    title= "RecoCore API",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)

@app.get("/")
def health_check():

    return {
        "success": True,
        "message": "RecoCore API is running"
    }