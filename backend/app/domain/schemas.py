"""Pydantic DTO：MQTT 消息体与 REST 请求/响应。字段对齐 schemas/ 与 04 契约。"""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

# ---- MQTT envelope / payloads ----

class Envelope(BaseModel):
    schema_version: str = "1.0"
    message_id: str
    device_id: str
    sent_at: datetime | None = None
    clock_synced: bool | None = None
    device_sequence: int | None = None
    type: str
    payload: dict[str, Any] = Field(default_factory=dict)


StudyAction = Literal["view_next", "flip", "mark_difficult", "skip", "session_complete"]
CommandType = Literal["content.sync", "device.config_update", "device.reboot", "ota.install"]
AckStatus = Literal["accepted", "succeeded", "rejected", "failed"]


class PresencePayload(BaseModel):
    online: bool
    firmware_version: str
    content_version: str
    network: str | None = None
    posture: str | None = None
    free_heap_bytes: int | None = None
    reset_reason: str | None = None


class StudyActionPayload(BaseModel):
    session_id: str
    bundle_version: str
    card_id: str
    card_type: str
    action: StudyAction
    device_sequence: int | None = None


class ContentSyncPayload(BaseModel):
    bundle_version: str
    url: str
    size_bytes: int
    sha256: str


class AckPayload(BaseModel):
    correlation_id: str
    status: AckStatus
    error_code: str | None = None
    detail: str | None = None


# ---- REST DTO ----

class PairingSessionCreate(BaseModel):
    device_name: str | None = None


class PairingSessionOut(BaseModel):
    session_id: str
    code: str
    expires_at: datetime


class PairingClaim(BaseModel):
    code: str
    device_id: str
    firmware_version: str | None = None


class PairingClaimOut(BaseModel):
    device_id: str
    credential: str
    message: str


class DeviceOut(BaseModel):
    id: str
    name: str | None = None
    firmware_version: str | None = None
    content_version: str | None = None
    last_seen_at: datetime | None = None
    online: bool = False


class ContentBundleCreate(BaseModel):
    version: str
    manifest_url: str | None = None
    sha256: str
    size_bytes: int
    object_key: str | None = None


class ContentBundleOut(BaseModel):
    id: str
    version: str
    sha256: str
    size_bytes: int
    status: str
    created_at: datetime


class ContentSyncRequest(BaseModel):
    bundle_version: str


class ContentSyncCommandOut(BaseModel):
    message_id: str
    command_type: str
    expires_at: datetime | None


class StudyEventOut(BaseModel):
    message_id: str
    device_id: str
    card_id: str | None = None
    action: str
    occurred_at: datetime | None = None
    received_at: datetime
