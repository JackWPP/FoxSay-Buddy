from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.domain.models import CardProgress, StudyEvent
from app.repositories.base import BaseRepository


class StudyEventRepository(BaseRepository):
    async def exists(self, message_id: str) -> bool:
        return await self.session.get(StudyEvent, message_id) is not None

    async def insert(self, event: StudyEvent) -> bool:
        """幂等插入：message_id 冲突（重投）返回 False。"""
        stmt = (
            insert(StudyEvent)
            .values(
                message_id=event.message_id,
                device_id=event.device_id,
                card_id=event.card_id,
                action=event.action,
                occurred_at=event.occurred_at,
                payload=event.payload,
            )
            .on_conflict_do_nothing(index_elements=["message_id"])
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def upsert_progress(
        self,
        device_id: str,
        card_id: str,
        *,
        difficulty: str | None = None,
    ) -> None:
        """更新 CardProgress 投影；revision 自增，难度在 None 时保留原值。"""
        now = datetime.now(UTC)
        stmt = (
            insert(CardProgress)
            .values(
                device_id=device_id,
                card_id=card_id,
                difficulty=difficulty,
                last_seen_at=now,
                revision=1,
            )
            .on_conflict_do_update(
                index_elements=["device_id", "card_id"],
                set_={
                    "difficulty": difficulty or CardProgress.difficulty,
                    "last_seen_at": now,
                    "revision": CardProgress.revision + 1,
                },
            )
        )
        await self.session.execute(stmt)

    async def list_by_device(
        self,
        device_id: str,
        *,
        limit: int = 100,
        offset: int = 0,
        card_id: str | None = None,
    ) -> list[StudyEvent]:
        stmt = (
            select(StudyEvent)
            .where(StudyEvent.device_id == device_id)
            .order_by(StudyEvent.received_at.desc())
            .limit(limit)
            .offset(offset)
        )
        if card_id is not None:
            stmt = stmt.where(StudyEvent.card_id == card_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_device(self, device_id: str, *, card_id: str | None = None) -> int:
        from sqlalchemy import func

        stmt = select(func.count()).select_from(StudyEvent).where(StudyEvent.device_id == device_id)
        if card_id is not None:
            stmt = stmt.where(StudyEvent.card_id == card_id)
        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    async def list_progress(
        self, device_id: str, *, limit: int = 100, offset: int = 0
    ) -> list[CardProgress]:
        stmt = (
            select(CardProgress)
            .where(CardProgress.device_id == device_id)
            .order_by(CardProgress.last_seen_at.desc().nullslast())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
