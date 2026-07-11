"""命令状态机：根据设备 ack 推进 DeviceCommand 状态。"""

from app.core.logging import get_logger
from app.domain.models import DeviceCommand
from app.repositories.command import DeviceCommandRepository

log = get_logger("app.domain.commands")

TERMINAL_STATUSES = {"succeeded", "failed", "rejected"}


class CommandService:
    def __init__(self, command_repo: DeviceCommandRepository) -> None:
        self.command_repo = command_repo

    async def apply_ack(
        self,
        correlation_id: str,
        status: str,
        error_code: str | None = None,
    ) -> DeviceCommand | None:
        """幂等推进命令状态；终态后再来 ack 不重复更新。"""
        command = await self.command_repo.get(correlation_id)
        if command is None:
            log.warning("ack_unknown_command", correlation_id=correlation_id)
            return None
        if command.status in TERMINAL_STATUSES:
            log.info("ack_duplicate", correlation_id=correlation_id, status=command.status)
            return command
        await self.command_repo.update_status(correlation_id, status)
        command.status = status
        log.info(
            "command_status_updated",
            correlation_id=correlation_id,
            status=status,
            error_code=error_code,
        )
        return command
