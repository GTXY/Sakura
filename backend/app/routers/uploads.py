import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File
import aiofiles

from app.config import settings
from app.schemas import UploadOut

router = APIRouter(prefix="/uploads", tags=["uploads"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


@router.post("", response_model=UploadOut, status_code=201)
async def upload_file(file: UploadFile = File(...)):
    """上傳圖片並返回可訪問的 URL（供新增店舖時設定封面圖使用）。"""
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail=f"不支援的格式：{file.content_type}")

    ext = Path(file.filename or "img").suffix or ".jpg"
    file_name = f"{uuid.uuid4().hex}{ext}"
    save_dir = Path(settings.upload_dir) / "temp"
    save_dir.mkdir(parents=True, exist_ok=True)
    save_path = save_dir / file_name

    async with aiofiles.open(save_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    return UploadOut(url=f"{settings.base_url}/uploads/temp/{file_name}")
