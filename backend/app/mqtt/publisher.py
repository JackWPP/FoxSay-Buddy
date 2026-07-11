"""MQTT 发布器：构造业务 ack / command envelope 并通过 bridge 发布。

不直接依赖 bridge 类型（避免循环 import），通过 Protocol 约束 sender。
"""

from datetime import UTC, datetime
from typing import Protocol

from ulid import ULID

from app.mqtt.bridge import DEVICE_TOPIC_PREFIX

SCHEMA_VERSION = "1.0"


def _now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


class SenderLike(Protocol):
    async def publish(self, topic: str, payload: dict, qos: int | None = None) -> None: ...


class Publisher:
    def __init__(self, sender: SenderLike) -> None:
        self.sender = sender

    async def publish_ack(
        self,
        device_id: str,
        correlation_id: str,
        status: str,
        *,
        error_code: str | None = None,
        detail: str | None = None,
    ) -> None:
        topic = f"{DEVICE_TOPIC_PREFIX}{device_id}/acks"
        envelope = {
            "schema_version": SCHEMA_VERSION,
            "message_id": f"ack_{ULID()}",
            "device_id": device_id,
            "sent_at": _now_iso(),
            "type": "message.ack",
            "payload": {
                "correlation_id": correlation_id,
                "status": status,
                "error_code": error_code,
                "detail": detail,
            },
        }
        await self.sender.publish(topic, envelope)

    async def publish_nack(self, device_id: str, correlation_id: str, error_code: str) -> None:
        await self.publish_ack(device_id, correlation_id, "rejected", error_code=error_code)

    async def publish_command(
        self,
        device_id: str,
        command_id: str,
        cmd_type: str,
        payload: dict,
        *,
        expires_at: datetime | None = None,
    ) -> None:
        topic = f"{DEVICE_TOPIC_PREFIX}{device_id}/commands"
        envelope = {
            "schema_version": SCHEMA_VERSION,
            "message_id": command_id,
            "device_id": device_id,
            "sent_at": _now_iso(),
            "expires_at": expires_at.isoformat(timespec="seconds").replace("+00:00", "Z")
            if expires_at
            else None,
            "type": cmd_type,
            "payload": payload,
        }
        await self.sender.publish(topic, envelope)
