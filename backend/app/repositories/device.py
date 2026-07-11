from datetime import UTC, datetime

from sqlalchemy import update

from app.domain.models import Device
from app.repositories.base import BaseRepository


class DeviceRepository(BaseRepository):
    async def get(self, device_id: str) -> Device | None:
        return await self.session.get(Device, device_id)

    async def create(
        self,
        device_id: str,
        name: str | None = None,
        firmware_version: str | None = None,
    ) -> Device:
        device = Device(id=device_id, name=name, firmware_version=firmware_version)
        self.session.add(device)
        await self.session.flush()
        return device

    async def touch(
        self,
        device_id: str,
        *,
        firmware_version: str | None = None,
        content_version: str | None = None,
    ) -> None:
        values: dict = {"last_seen_at": datetime.now(UTC)}
        if firmware_version is not None:
            values["firmware_version"] = firmware_version
        if content_version is not None:
            values["content_version"] = content_version
        await self.session.execute(
            update(Device).where(Device.id == device_id).values(**values)
        )
