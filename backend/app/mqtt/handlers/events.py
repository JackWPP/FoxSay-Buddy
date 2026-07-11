"""学习事件处理：幂等入库 + CardProgress 投影。

ack 不在此处发送，由 router 在 DB commit 成功后统一发送，
避免"已回 ack 但未落库"导致设备清空 outbox 却丢数据。
"""

from app.core.logging import get_logger
from app.domain.schemas import Envelope
from app.domain.services.study_events import StudyEventService
from app.repositories.device import DeviceRepository
from app.repositories.study_event import StudyEventRepository

log = get_logger("app.mqtt.events")


class EventsHandler:
    def __init__(self, session) -> None:
        self.session = session

    async def handle(self, envelope: Envelope) -> bool:
        service = StudyEventService(
            DeviceRepository(self.session),
            StudyEventRepository(self.session),
        )
        created = await service.ingest(envelope)
        log.info(
            "event_ingested",
            message_id=envelope.message_id,
            device_id=envelope.device_id,
            created=created,
        )
        return created
