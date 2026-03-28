from fastapi import APIRouter
from app.service.animal_service import animal_service

router = APIRouter(prefix="/animal", tags=["animal"])


@router.get("")
def animal():
    return animal_service.get_animal()


@router.post("")
def animal(message: str = "OK", value: int = 0):
    animal_service.set_animal(message, value)
    return {"status": "ok"}
