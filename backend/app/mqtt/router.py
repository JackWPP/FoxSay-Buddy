"""MQTT topic 路由：校验 topic / envelope / device 身份，分发到 handlers。

每条消息在独立 DB session 中处理并提交。AGENTS.md：消费事件幂等，
DB 更新与后续发布用事务/outbox 避免已写库未回 ack。
"""

import re

from app.core.logging import get_logger
from app.domain.schemas import Envelope
from app.mqtt.handlers.acks import AcksHandler
from app.mqtt.handlers.events import EventsHandler
from app.mqtt.handlers.presence import PresenceHandler

log = get_logger("app.mqtt.router")

TOPIC_RE = re.compile(
    r"^foxsay/v1/devices/(?P<device_id>[^/]+)/(?P<suffix>presence|events|acks)$"
)


class MQTTRouter:
    def __init__(self, session_factory, publisher) -> None:
        self.session_factory = session_factory
        self.publisher = publisher

    async def route(self, topic: str, data: dict) -> None:
        m = TOPIC_RE.match(topic)
        if not m:
            log.warning("topic_unmatched", topic=topic)
            return
        device_id = m.group("device_id")
        suffix = m.group("suffix")

        try:
            envelope = Envelope(**data)
        except Exception as e:  # noqa: BLE001
            log.warning("envelope_invalid", topic=topic, error=str(e))
            await self.publisher.publish_nack(
                device_id, data.get("message_id", ""), "invalid_payload"
            )
            return

        if envelope.device_id != device_id:
            log.warning(
                "device_id_mismatch",
                topic_device=device_id,
                envelope_device=envelope.device_id,
            )
            return

        async with self.session_factory() as session:
            try:
                if suffix == "presence":
                    await PresenceHandler(session).handle(envelope)
                elif suffix == "events":
                    await EventsHandler(session).handle(envelope)
                elif suffix == "acks":
                    await AcksHandler(session).handle(envelope)
                await session.commit()
            except Exception as e:  # noqa: BLE001
                await session.rollback()
                log.error(
                    "handler_failed",
                    suffix=suffix,
                    message_id=envelope.message_id,
                    error=str(e),
                )
                # 事件处理失败：回 failed ack，设备可按策略重试；其他 suffix 不回 ack
                if suffix == "events":
                    await self.publisher.publish_ack(
                        envelope.device_id,
                        envelope.message_id,
                        "failed",
                        error_code="internal_error",
                        detail=str(e),
                    )
                return
            # commit 成功后回 events 业务 ack（避免已发 ack 但未落库）
            if suffix == "events":
                await self.publisher.publish_ack(
                    envelope.device_id, envelope.message_id, "succeeded"
                )
