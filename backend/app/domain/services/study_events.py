"""学习事件领域服务：幂等入库 + CardProgress 投影。"""

from app.core.logging import get_logger
from app.domain.models import StudyEvent
from app.domain.schemas import Envelope, StudyActionPayload
from app.repositories.device import DeviceRepository
from app.repositories.study_event import StudyEventRepository

log = get_logger("app.domain.study_events")

DIFFICULT_ACTIONS = {"mark_difficult"}


class StudyEventService:
    def __init__(self, device_repo: DeviceRepository, event_repo: StudyEventRepository) -> None:
        self.device_repo = device_repo
        self.event_repo = event_repo

    async def ingest(self, envelope: Envelope) -> bool:
        """幂等入库并更新投影。返回 True=新增，False=重投（不重复计数）。"""
        payload = StudyActionPayload(**envelope.payload)
        occurred_at = envelope.sent_at if envelope.clock_synced else None

        # 设备不存在则登记（local 无鉴权，任意 device_id 可上报）
        device = await self.device_repo.get(envelope.device_id)
        if device is None:
            await self.device_repo.create(envelope.device_id)

        event = StudyEvent(
            message_id=envelope.message_id,
            device_id=envelope.device_id,
            card_id=payload.card_id,
            action=payload.action,
            occurred_at=occurred_at,
            payload=envelope.payload,
        )
        created = await self.event_repo.insert(event)
        if not created:
            log.info(
                "study_event_duplicate",
                message_id=envelope.message_id,
                device_id=envelope.device_id,
            )
            return False

        difficulty = "difficult" if payload.action in DIFFICULT_ACTIONS else None
        await self.event_repo.upsert_progress(
            envelope.device_id, payload.card_id, difficulty=difficulty
        )
        log.info(
            "study_event_ingested",
            message_id=envelope.message_id,
            device_id=envelope.device_id,
            action=payload.action,
            card_id=payload.card_id,
        )
        return True
