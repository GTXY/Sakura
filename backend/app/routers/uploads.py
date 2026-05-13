import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File

from app.config import settings
from app.deps import get_current_user
from app.gcs import object_to_url, upload_file
from app.models import User
from app.schemas import UploadOut

router = APIRouter(prefix="/uploads", tags=["uploads"])

ALLOWED_TYPES = {"image/jpeg", "image/png"}
MAX_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("", response_model=UploadOut, status_code=201)
async def upload_cover(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """上傳封面圖（臨時暫存），返回 GCS 簽名 URL。需要登入。"""
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail="只接受 JPG 或 PNG 格式")

    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=413, detail="檔案大小不能超過 10 MB")

    ext = ".jpg" if file.content_type == "image/jpeg" else ".png"
    object_name = f"temp/{uuid.uuid4().hex}{ext}"

    upload_file(settings.gcs_bucket_name, object_name, content, file.content_type)
    return UploadOut(url=object_to_url(settings.gcs_bucket_name, object_name))
