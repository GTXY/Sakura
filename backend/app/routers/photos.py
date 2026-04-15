import uuid
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import aiofiles

from app.config import settings
from app.database import get_db
from app.models import Shop, ShopPhoto
from app.schemas import PhotoOut

router = APIRouter(prefix="/shops/{shop_id}/photos", tags=["photos"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


async def _save_file(shop_id: UUID, file: UploadFile) -> str:
    ext = Path(file.filename or "img").suffix or ".jpg"
    file_name = f"{uuid.uuid4().hex}{ext}"
    save_dir = Path(settings.upload_dir) / "shops" / str(shop_id)
    save_dir.mkdir(parents=True, exist_ok=True)
    save_path = save_dir / file_name

    async with aiofiles.open(save_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    return f"{settings.base_url}/uploads/shops/{shop_id}/{file_name}"


# ── POST /api/shops/{shop_id}/photos ────────────────────────────
@router.post("", response_model=list[PhotoOut], status_code=201)
async def upload_photos(
    shop_id: UUID,
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Shop).where(Shop.id == shop_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="店舖不存在")

    # Determine current max sort_order
    max_order_result = await db.execute(
        select(ShopPhoto.sort_order)
        .where(ShopPhoto.shop_id == shop_id)
        .order_by(ShopPhoto.sort_order.desc())
        .limit(1)
    )
    max_order = max_order_result.scalar_one_or_none() or -1

    saved: list[PhotoOut] = []
    for i, file in enumerate(files):
        if file.content_type not in ALLOWED_TYPES:
            raise HTTPException(status_code=415, detail=f"不支援的圖片格式：{file.content_type}")

        url = await _save_file(shop_id, file)
        photo = ShopPhoto(shop_id=shop_id, url=url, sort_order=max_order + 1 + i)
        db.add(photo)
        await db.flush()
        saved.append(PhotoOut(id=photo.id, url=photo.url, sort_order=photo.sort_order))

    await db.commit()
    return saved


# ── DELETE /api/shops/{shop_id}/photos/{photo_id} ───────────────
@router.delete("/{photo_id}", status_code=204)
async def delete_photo(shop_id: UUID, photo_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ShopPhoto).where(ShopPhoto.id == photo_id, ShopPhoto.shop_id == shop_id)
    )
    photo = result.scalar_one_or_none()
    if not photo:
        raise HTTPException(status_code=404, detail="相片不存在")

    # Best-effort: remove local file
    url_path = photo.url.replace(settings.base_url, "").lstrip("/")
    local_file = Path(url_path)
    if local_file.exists():
        local_file.unlink(missing_ok=True)

    await db.delete(photo)
    await db.commit()
