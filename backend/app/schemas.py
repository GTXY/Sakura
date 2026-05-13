from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    """Base model: snake_case in Python ↔ camelCase in JSON."""
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


# ── Auth ─────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: UUID
    username: str

    model_config = ConfigDict(from_attributes=True)


# ── Photos ──────────────────────────────────────────────────────

class PhotoOut(CamelModel):
    id: UUID
    url: str
    sort_order: int


# ── Shops ───────────────────────────────────────────────────────

class ShopOut(CamelModel):
    id: UUID
    name: str
    prefecture: str
    city: str
    address: str | None = None
    category: str
    tag: str
    phone: str | None = None
    hours: str | None = None
    lat: float
    lng: float
    cover_image: str
    one_liner: str
    description: str
    rating: float
    visit_date: date
    featured: bool
    photos: list[str] = []
    created_at: datetime
    updated_at: datetime

    @field_validator("lat", "lng", "rating", mode="before")
    @classmethod
    def decimal_to_float(cls, v):
        return float(v) if v is not None else v


class ShopCreate(CamelModel):
    name: str
    prefecture: str
    city: str
    address: str | None = None
    category: str
    tag: str
    phone: str | None = None
    hours: str | None = None
    lat: float
    lng: float
    cover_image: str
    one_liner: str
    description: str
    rating: float
    visit_date: date
    featured: bool = False


class ShopUpdate(CamelModel):
    name: str | None = None
    prefecture: str | None = None
    city: str | None = None
    address: str | None = None
    category: str | None = None
    tag: str | None = None
    phone: str | None = None
    hours: str | None = None
    lat: float | None = None
    lng: float | None = None
    cover_image: str | None = None
    one_liner: str | None = None
    description: str | None = None
    rating: float | None = None
    visit_date: date | None = None
    featured: bool | None = None


# ── Stats ────────────────────────────────────────────────────────

class StatsOut(BaseModel):
    total: int
    prefectures: int


# ── Upload ───────────────────────────────────────────────────────

class UploadOut(BaseModel):
    url: str
