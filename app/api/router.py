from fastapi import APIRouter
from app.api.v1 import frame, animal

api_router = APIRouter()
api_router.include_router(frame.router)
api_router.include_router(animal.router)
