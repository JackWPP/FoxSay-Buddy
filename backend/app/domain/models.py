"""SQLAlchemy 2.0 ORM 实体。

对应 docs/specs/02-system-architecture.md §4 数据模型（ADR-008：无 User）。
StudyEvent.message_id 为 QoS1 幂等键；CardProgress 为事件投影，不替代审计。
"""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    type_annotation_map = {dict[str, Any]: JSONB}


def utcnow() -> datetime:
    return datetime.now(UTC)


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    firmware_version: Mapped[str | None] = mapped_column(String, nullable=True)
    content_version: Mapped[str | None] = mapped_column(String, nullable=True)
    credential_version: Mapped[int] = mapped_column(Integer, default=1)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    pairing_sessions: Mapped[list["PairingSession"]] = relationship(back_populates="device")


class PairingSession(Base):
    __tablename__ = "pairing_sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    code_hash: Mapped[str] = mapped_column(String, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    claimed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    claimed_device_id: Mapped[str | None] = mapped_column(
        ForeignKey("devices.id"), nullable=True
    )
    device: Mapped["Device | None"] = relationship(back_populates="pairing_sessions")


class ContentBundle(Base):
    __tablename__ = "content_bundles"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    version: Mapped[str] = mapped_column(String, unique=True, index=True)
    object_key: Mapped[str | None] = mapped_column(String, nullable=True)
    manifest_url: Mapped[str] = mapped_column(Text)
    sha256: Mapped[str] = mapped_column(String(64))
    size_bytes: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String, default="created")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    cards: Mapped[list["Card"]] = relationship(back_populates="bundle")


class Card(Base):
    __tablename__ = "cards"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    bundle_id: Mapped[str] = mapped_column(ForeignKey("content_bundles.id"))
    type: Mapped[str] = mapped_column(String)
    front: Mapped[dict[str, Any]] = mapped_column(JSONB)
    back: Mapped[dict[str, Any]] = mapped_column(JSONB)
    assets: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    bundle: Mapped["ContentBundle"] = relationship(back_populates="cards")


class StudyEvent(Base):
    __tablename__ = "study_events"

    message_id: Mapped[str] = mapped_column(String, primary_key=True)
    device_id: Mapped[str] = mapped_column(String, ForeignKey("devices.id"), index=True)
    card_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    action: Mapped[str] = mapped_column(String)
    occurred_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)


class CardProgress(Base):
    __tablename__ = "card_progress"

    device_id: Mapped[str] = mapped_column(String, ForeignKey("devices.id"), primary_key=True)
    card_id: Mapped[str] = mapped_column(String, primary_key=True)
    difficulty: Mapped[str | None] = mapped_column(String, nullable=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revision: Mapped[int] = mapped_column(Integer, default=0)


class DeviceCommand(Base):
    __tablename__ = "device_commands"

    message_id: Mapped[str] = mapped_column(String, primary_key=True)
    device_id: Mapped[str] = mapped_column(String, ForeignKey("devices.id"), index=True)
    type: Mapped[str] = mapped_column(String)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String, default="pending")
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
