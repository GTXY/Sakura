import uuid
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.deps import get_current_user
from app.gcs import delete_file, object_to_url, upload_file
from app.models import Shop, ShopPhoto, User
from app.schemas import PhotoOut

router = APIRouter(prefix="/shops/{shop_id}/photos", tags=["photos"])

ALLOWED_TYPES = {"image/jpeg", "image/png"}
MAX_SIZE = 10 * 1024 * 1024  # 10 MB


async def _upload_photo(shop_id: UUID, file: UploadFile) -> str:
    """Upload one photo to GCS and return the object path."""
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=413, detail=f"{file.filename} 超過 10 MB 限制")

    ext = ".jpg" if file.content_type == "image/jpeg" else ".png"
    object_name = f"shops/{shop_id}/{uuid.uuid4().hex}{ext}"
    upload_file(settings.gcs_bucket_name, object_name, content, file.content_type)
    return object_name


# ── POST /api/shops/{shop_id}/photos ────────────────────────────
@router.post("", response_model=list[PhotoOut], status_code=201)
async def upload_photos(
    shop_id: UUID,
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Shop).where(Shop.id == shop_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="店舖不存在")

    for file in files:
        if file.content_type not in ALLOWED_TYPES:
            raise HTTPException(status_code=415, detail=f"{file.filename} 只接受 JPG 或 PNG 格式")

    max_order_result = await db.execute(
        select(ShopPhoto.sort_order)
        .where(ShopPhoto.shop_id == shop_id)
        .order_by(ShopPhoto.sort_order.desc())
        .limit(1)
    )
    max_order = max_order_result.scalar_one_or_none() or -1

    saved: list[PhotoOut] = []
    for i, file in enumerate(files):
        object_name = await _upload_photo(shop_id, file)
        photo = ShopPhoto(shop_id=shop_id, url=object_name, sort_order=max_order + 1 + i)
        db.add(photo)
        await db.flush()
        saved.append(PhotoOut(
            id=photo.id,
            url=object_to_url(settings.gcs_bucket_name, photo.url),
            sort_order=photo.sort_order,
        ))

    await db.commit()
    return saved


# ── DELETE /api/shops/{shop_id}/photos/{photo_id} ───────────────
@router.delete("/{photo_id}", status_code=204)
async def delete_photo(
    shop_id: UUID,
    photo_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ShopPhoto).where(ShopPhoto.id == photo_id, ShopPhoto.shop_id == shop_id)
    )
    photo = result.scalar_one_or_none()
    if not photo:
        raise HTTPException(status_code=404, detail="相片不存在")

    if not photo.url.startswith("http"):
        delete_file(settings.gcs_bucket_name, photo.url)

    await db.delete(photo)
    await db.commit()
