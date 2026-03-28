from fastapi import APIRouter


class AnimalService:
    def __init__(self):
        self.message = "Hello, World!"
        self.counter = 0

    def get_animal(self):
        return {"status": "ok", "data": {"message": self.message, "value": self.counter}}

    def set_animal(self, message, value):
        self.message = message
        self.counter = value


animal_service = AnimalService()
