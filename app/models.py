
from __future__ import annotations

import asyncio
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import UUID, ForeignKey, Integer, String, func, select
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    validates,
)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class BaseModel(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now())




class Batch(Base):
    __tablename__ = "batches"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status: Mapped[str] = mapped_column(String, default="processing")
    webhook_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())

    products: Mapped[List["Product"]] = relationship("Product", back_populates="batch")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    batch_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("batches.id"))
    serial_number: Mapped[int] = mapped_column(Integer)
    product_name: Mapped[str] = mapped_column(String)
    input_image_urls: Mapped[List[str]] = mapped_column(ARRAY(String))
    output_image_urls: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=True)

    batch: Mapped["Batch"] = relationship("Batch", back_populates="products")
    images: Mapped[List["Image"]] = relationship("Image", back_populates="product")

# Image model
class Image(Base):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"))
    input_url: Mapped[str] = mapped_column(String)
    output_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="pending")

    product: Mapped["Product"] = relationship("Product", back_populates="images")
