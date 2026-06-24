from typing import Annotated
from fastapi import APIRouter, UploadFile, File, Depends, Query, status
from app.core.cloudinary import upload_image, delete_image, extract_public_id
from app.core.deps import require_role
from app.modules.usuarios.schemas import UserPublic

router = APIRouter(prefix="/upload", tags=["upload"])


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
