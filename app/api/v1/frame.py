from fastapi.responses import StreamingResponse
from fastapi.requests import Request
from fastapi.routing import APIRouter
from starlette import status

from app.service.frame_service import frame_service

router = APIRouter(prefix="/frame", tags=["frame"])


@router.post(path="", status_code=status.HTTP_200_OK)
async def upload_frame(request: Request):
    return await frame_service.receive_frame(request)


@router.get(path="/stream", status_code=status.HTTP_200_OK)
async def stream_frame():
    return StreamingResponse(
        frame_service.stream_frame(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@router.get(path="/status", status_code=status.HTTP_200_OK)
async def get_status():
    return frame_service.get_stats()
