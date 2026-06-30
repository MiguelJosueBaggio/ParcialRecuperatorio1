import time
import hashlib
from typing import Annotated, Optional
from fastapi import APIRouter, UploadFile, File, Depends, Query, status, Body
from pydantic import BaseModel
import cloudinary.utils
from app.core.cloudinary import upload_image, delete_image, extract_public_id
from app.core.config import settings
from app.core.deps import require_role
from app.modules.usuarios.schemas import UserPublic

router = APIRouter(prefix="/upload", tags=["upload"])


class FirmaRequest(BaseModel):
    folder: Optional[str] = None


class FirmaResponse(BaseModel):
    signature: str
    timestamp: int
    api_key: str
    cloud_name: str


@router.post("/firma/", response_model=FirmaResponse, summary="Genera firma para upload directo a Cloudinary")
async def generar_firma(
    body: FirmaRequest = Body(default=FirmaRequest()),
    _: Annotated[UserPublic, Depends(require_role(["ADMIN"]))] = None,
) -> FirmaResponse:
    timestamp = int(time.time())
    params_to_sign: dict = {"timestamp": timestamp}
    if body.folder:
        params_to_sign["folder"] = body.folder

    signature = cloudinary.utils.api_sign_request(params_to_sign, settings.CLOUDINARY_API_SECRET)

    return FirmaResponse(
        signature=signature,
        timestamp=timestamp,
        api_key=settings.CLOUDINARY_API_KEY,
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload(
    file: UploadFile = File(...),
    folder: str = Query(default="foodstore", max_length=50),
    _: Annotated[UserPublic, Depends(require_role(["ADMIN", "STOCK"]))] = None,
):
    result = upload_image(file, folder)
    return result


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    url: str = Query(..., min_length=10),
    _: Annotated[UserPublic, Depends(require_role(["ADMIN", "STOCK"]))] = None,
):
    public_id = extract_public_id(url)
    if public_id:
        delete_image(public_id)
