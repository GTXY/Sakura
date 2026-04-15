import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, ForeignKey, Numeric, SmallInteger, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Shop(Base):
    __tablename__ = "shops"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100))
    prefecture: Mapped[str] = mapped_column(String(20))
    city: Mapped[str] = mapped_column(String(50))
    category: Mapped[str] = mapped_column(String(20))
    tag: Mapped[str] = mapped_column(String(30))
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    hours: Mapped[str | None] = mapped_column(String(100), nullable=True)
    lat: Mapped[Decimal] = mapped_column(Numeric(9, 6))
    lng: Mapped[Decimal] = mapped_column(Numeric(9, 6))
    cover_image: Mapped[str] = mapped_column(Text)
    one_liner: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    rating: Mapped[Decimal] = mapped_column(Numeric(3, 1))
    visit_date: Mapped[date] = mapped_column(Date)
    featured: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    photos: Mapped[list["ShopPhoto"]] = relationship(
        "ShopPhoto",
        back_populates="shop",
        order_by="ShopPhoto.sort_order",
        cascade="all, delete-orphan",
    )


class ShopPhoto(Base):
    __tablename__ = "shop_photos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("shops.id", ondelete="CASCADE"))
    url: Mapped[str] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(SmallInteger, default=0)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    shop: Mapped["Shop"] = relationship("Shop", back_populates="photos")
