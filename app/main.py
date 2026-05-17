from fastapi import FastAPI

from app.db import engine
from app.models import Item, User, Interaction
from app.models.base import Base

from app.routes import router as interaction_router


app = FastAPI(
    title= "RecoCore API",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)

app.include_router(interaction_router)

@app.get("/")
def health_check():

    return {
        "success": True,
        "message": "RecoCore API is running"
    }