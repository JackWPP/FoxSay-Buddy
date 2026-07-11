from datetime import UTC, datetime, timedelta

from sqlalchemy import select, update

from app.core.config import settings
from app.domain.models import PairingSession
from app.repositories.base import BaseRepository


class PairingSessionRepository(BaseRepository):
    async def create(
        self,
        session_id: str,
        code_hash: str,
        ttl_seconds: int | None = None,
    ) -> PairingSession:
        ttl = ttl_seconds if ttl_seconds is not None else settings.pairing_code_ttl_seconds
        ps = PairingSession(
            id=session_id,
            code_hash=code_hash,
            expires_at=datetime.now(UTC) + timedelta(seconds=ttl),
        )
        self.session.add(ps)
        await self.session.flush()
        return ps

    async def get(self, session_id: str) -> PairingSession | None:
        return await self.session.get(PairingSession, session_id)

    async def get_by_code_hash(self, code_hash: str) -> PairingSession | None:
        result = await self.session.execute(
            select(PairingSession).where(PairingSession.code_hash == code_hash)
        )
        return result.scalar_one_or_none()

    async def claim(self, session_id: str, device_id: str) -> None:
        now = datetime.now(UTC)
        await self.session.execute(
            update(PairingSession)
            .where(PairingSession.id == session_id)
            .values(claimed_at=now, claimed_device_id=device_id)
        )
