import cloudinary
import cloudinary.uploader
import cloudinary.api
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)


def upload_image(file: UploadFile, folder: str = "foodstore") -> dict:
    allowed = {"image/jpeg", "image/png", "image/webp", "image/gif"}
    if file.content_type not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato no soportado: {file.content_type}. Usá JPEG, PNG, WebP o GIF.",
        )

    result = cloudinary.uploader.upload(
        file.file,
        folder=folder,
        resource_type="image",
    )

    return {
        "url": result["secure_url"],
        "public_id": result["public_id"],
    }


def delete_image(public_id: str) -> None:
    cloudinary.uploader.destroy(public_id)


def extract_public_id(url: str) -> str | None:
    if "res.cloudinary.com" not in url:
        return None
    parts = url.split("/")
    if len(parts) < 2:
        return None
    return "/".join(parts[-2:]).rsplit(".", 1)[0]
