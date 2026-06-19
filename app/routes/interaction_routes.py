from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import DataResponse
from app.schemas import InteractionCreate, InteractionResponse

from app.services import create_interaction

interaction_router = APIRouter(
    prefix="/interactions",
    tags=["Interactions"]
)

@interaction_router.post(
    "", 
    response_model=DataResponse[InteractionResponse], 
    status_code=status.HTTP_201_CREATED)
def create_interaction_route(payload: InteractionCreate,
                             db: Session = Depends(get_db)
):
    try:
        interaction = create_interaction(
            payload=payload,
            db=db
        )

        return {
            "success": True,
            "message": "Interaction created successfully",
            "data": interaction
        }
    
    except ValueError as error:

        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )
