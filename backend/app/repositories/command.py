from sqlalchemy import update

from app.domain.models import DeviceCommand
from app.repositories.base import BaseRepository


class DeviceCommandRepository(BaseRepository):
    async def create(self, command: DeviceCommand) -> DeviceCommand:
        self.session.add(command)
        await self.session.flush()
        return command

    async def get(self, message_id: str) -> DeviceCommand | None:
        return await self.session.get(DeviceCommand, message_id)

    async def update_status(self, message_id: str, status: str) -> None:
        await self.session.execute(
            update(DeviceCommand)
            .where(DeviceCommand.message_id == message_id)
            .values(status=status)
        )
