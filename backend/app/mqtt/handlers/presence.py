"""presence 消息处理：更新设备在线状态与版本，刷新 last_seen。"""

from app.core.logging import get_logger
from app.domain.schemas import Envelope, PresencePayload
from app.repositories.device import DeviceRepository

log = get_logger("app.mqtt.presence")


class PresenceHandler:
    def __init__(self, session) -> None:
        self.session = session

    async def handle(self, envelope: Envelope) -> None:
        payload = PresencePayload(**envelope.payload)
        repo = DeviceRepository(self.session)
        device = await repo.get(envelope.device_id)
        if device is None:
            await repo.create(
                envelope.device_id, firmware_version=payload.firmware_version
            )
        else:
            await repo.touch(
                envelope.device_id,
                firmware_version=payload.firmware_version,
                content_version=payload.content_version,
            )
        log.info(
            "presence_updated",
            device_id=envelope.device_id,
            online=payload.online,
            firmware=payload.firmware_version,
        )
