"""命令 outbox 重试 worker。

定时扫描 status=accepted 且未到 expires_at 的 DeviceCommand,重新通过 MQTT 下发。
解决"设备离线期间命令丢失 / 服务端 publish 时 broker 未连"的可靠性问题。

幂等保证:
- 命令 message_id 不变,重投同一条命令;
- 设备侧按 message_id 去重(FW-NET-04),重投不重复执行;
- expires_at 过期后标 expired,不再重发。
"""

import asyncio
from datetime import UTC, datetime

from sqlalchemy import select, update

from app.core.logging import get_logger
from app.domain.models import DeviceCommand
from app.mqtt.publisher import Publisher

log = get_logger("app.workers.command_outbox")

RETRY_INTERVAL_SECONDS = 30
MAX_RESEND_AGE_SECONDS = 3600


class CommandOutboxWorker:
    """扫未终态命令,重发或过期。需要 broker publisher 和 session_factory。"""

    def __init__(self, session_factory, publisher: Publisher) -> None:
        self.session_factory = session_factory
        self.publisher = publisher
        self._task: asyncio.Task | None = None
        self._stop = asyncio.Event()

    async def start(self) -> None:
        self._task = asyncio.create_task(self._run(), name="command-outbox")
        log.info("command_outbox_worker_started", interval=RETRY_INTERVAL_SECONDS)

    async def stop(self) -> None:
        self._stop.set()
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except (asyncio.CancelledError, Exception):
                pass

    async def _run(self) -> None:
        while not self._stop.is_set():
            try:
                await self._sweep()
            except asyncio.CancelledError:
                raise
            except Exception as e:  # noqa: BLE001
                log.error("command_outbox_sweep_failed", error=str(e))
            await asyncio.sleep(RETRY_INTERVAL_SECONDS)

    async def _sweep(self) -> None:
        now = datetime.now(UTC)
        async with self.session_factory() as session:
            # 1. 过期未终态命令 -> expired
            expired_stmt = (
                update(DeviceCommand)
                .where(
                    DeviceCommand.expires_at.is_not(None),
                    DeviceCommand.expires_at < now,
                    DeviceCommand.status.in_(("pending", "accepted")),
                )
                .values(status="expired")
                .returning(DeviceCommand.message_id)
            )
            expired = (await session.execute(expired_stmt)).scalars().all()
            if expired:
                log.info("commands_expired", count=len(expired), ids=list(expired))

            # 2. 未终态且未过期的命令 -> 重发(同 message_id,设备去重)
            resend_stmt = (
                select(DeviceCommand)
                .where(DeviceCommand.status.in_(("pending", "accepted")))
                .order_by(DeviceCommand.sent_at.asc())
                .limit(100)
            )
            pending = list((await session.execute(resend_stmt)).scalars().all())
            await session.commit()

        for cmd in pending:
            if cmd.expires_at is not None and cmd.expires_at < now:
                continue
            try:
                await self.publisher.publish_command(
                    cmd.device_id,
                    cmd.message_id,
                    cmd.type,
                    cmd.payload,
                    expires_at=cmd.expires_at,
                )
                log.info(
                    "command_resent",
                    message_id=cmd.message_id,
                    device_id=cmd.device_id,
                    type=cmd.type,
                )
            except Exception as e:  # noqa: BLE001
                log.warning(
                    "command_resent_failed",
                    message_id=cmd.message_id,
                    error=str(e),
                )
