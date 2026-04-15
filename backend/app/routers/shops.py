from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Shop, ShopPhoto
from app.schemas import ShopCreate, ShopOut, ShopUpdate, StatsOut

router = APIRouter(prefix="/shops", tags=["shops"])

VALID_CATEGORIES = {"餐飲", "購物", "娛樂", "美容養生", "生活服務", "文化藝術", "自然景點", "住宿"}


def _shop_to_out(shop: Shop) -> ShopOut:
    return ShopOut.model_validate(
        {**shop.__dict__, "photos": [p.url for p in shop.photos]}
    )


# ── GET /api/shops ───────────────────────────────────────────────
@router.get("", response_model=list[ShopOut])
async def list_shops(
    sort: Literal["recent", "rating", "featured"] = "recent",
    category: str | None = Query(default=None),
    prefecture: str | None = Query(default=None),
    q: str | None = Query(default=None, description="搜尋關鍵字"),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Shop).options(selectinload(Shop.photos))

    if category:
        stmt = stmt.where(Shop.category == category)
    if prefecture:
        stmt = stmt.where(Shop.prefecture == prefecture)
    if q:
        pattern = f"%{q}%"
        stmt = stmt.where(
            Shop.name.ilike(pattern)
            | Shop.one_liner.ilike(pattern)
            | Shop.description.ilike(pattern)
            | Shop.tag.ilike(pattern)
            | Shop.prefecture.ilike(pattern)
            | Shop.city.ilike(pattern)
        )

    if sort == "rating":
        stmt = stmt.order_by(Shop.rating.desc())
    elif sort == "featured":
        stmt = stmt.order_by(Shop.featured.desc(), Shop.visit_date.desc())
    else:
        stmt = stmt.order_by(Shop.visit_date.desc())

    stmt = stmt.limit(limit).offset(offset)

    result = await db.execute(stmt)
    return [_shop_to_out(s) for s in result.scalars().all()]


# ── GET /api/shops/stats ─────────────────────────────────────────
@router.get("/stats", response_model=StatsOut)
async def get_stats(db: AsyncSession = Depends(get_db)):
    total = await db.scalar(select(func.count()).select_from(Shop))
    prefectures = await db.scalar(
        select(func.count(func.distinct(Shop.prefecture))).select_from(Shop)
    )
    return StatsOut(total=total or 0, prefectures=prefectures or 0)


# ── GET /api/shops/{id} ──────────────────────────────────────────
@router.get("/{shop_id}", response_model=ShopOut)
async def get_shop(shop_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Shop).options(selectinload(Shop.photos)).where(Shop.id == shop_id)
    )
    shop = result.scalar_one_or_none()
    if not shop:
        raise HTTPException(status_code=404, detail="店舖不存在")
    return _shop_to_out(shop)


# ── POST /api/shops ──────────────────────────────────────────────
@router.post("", response_model=ShopOut, status_code=201)
async def create_shop(body: ShopCreate, db: AsyncSession = Depends(get_db)):
    if body.category not in VALID_CATEGORIES:
        raise HTTPException(status_code=422, detail=f"無效的分類：{body.category}")
    if not (0.0 <= body.rating <= 5.0):
        raise HTTPException(status_code=422, detail="評分需在 0.0 ~ 5.0 之間")

    shop = Shop(**body.model_dump(by_alias=False))
    db.add(shop)
    await db.commit()
    await db.refresh(shop)

    result = await db.execute(
        select(Shop).options(selectinload(Shop.photos)).where(Shop.id == shop.id)
    )
    return _shop_to_out(result.scalar_one())


# ── PUT /api/shops/{id} ──────────────────────────────────────────
@router.put("/{shop_id}", response_model=ShopOut)
async def update_shop(shop_id: UUID, body: ShopUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Shop).options(selectinload(Shop.photos)).where(Shop.id == shop_id)
    )
    shop = result.scalar_one_or_none()
    if not shop:
        raise HTTPException(status_code=404, detail="店舖不存在")

    updates = body.model_dump(exclude_none=True, by_alias=False)
    if "category" in updates and updates["category"] not in VALID_CATEGORIES:
        raise HTTPException(status_code=422, detail=f"無效的分類：{updates['category']}")
    if "rating" in updates and not (0.0 <= updates["rating"] <= 5.0):
        raise HTTPException(status_code=422, detail="評分需在 0.0 ~ 5.0 之間")

    for key, val in updates.items():
        setattr(shop, key, val)

    await db.commit()
    await db.refresh(shop)

    result = await db.execute(
        select(Shop).options(selectinload(Shop.photos)).where(Shop.id == shop_id)
    )
    return _shop_to_out(result.scalar_one())


# ── DELETE /api/shops/{id} ───────────────────────────────────────
@router.delete("/{shop_id}", status_code=204)
async def delete_shop(shop_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Shop).where(Shop.id == shop_id))
    shop = result.scalar_one_or_none()
    if not shop:
        raise HTTPException(status_code=404, detail="店舖不存在")
    await db.delete(shop)
    await db.commit()
