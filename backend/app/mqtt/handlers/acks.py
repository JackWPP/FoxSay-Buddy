"""业务 ack 处理：推进 DeviceCommand 状态机。"""

from app.core.logging import get_logger
from app.domain.schemas import AckPayload, Envelope
from app.domain.services.commands import CommandService
from app.repositories.command import DeviceCommandRepository

log = get_logger("app.mqtt.acks")


class AcksHandler:
    def __init__(self, session) -> None:
        self.session = session

    async def handle(self, envelope: Envelope) -> None:
        payload = AckPayload(**envelope.payload)
        service = CommandService(DeviceCommandRepository(self.session))
        await service.apply_ack(
            correlation_id=payload.correlation_id,
            status=payload.status,
            error_code=payload.error_code,
        )
        log.info(
            "ack_applied",
            correlation_id=payload.correlation_id,
            status=payload.status,
            device_id=envelope.device_id,
        )
