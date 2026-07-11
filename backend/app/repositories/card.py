from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.domain.models import Card
from app.repositories.base import BaseRepository


class CardRepository(BaseRepository):
    async def get(self, card_id: str) -> Card | None:
        return await self.session.get(Card, card_id)

    async def create(self, card: Card) -> Card:
        self.session.add(card)
        await self.session.flush()
        return card

    async def list_by_bundle(
        self, bundle_id: str, *, limit: int = 100, offset: int = 0
    ) -> list[Card]:
        result = await self.session.execute(
            select(Card)
            .where(Card.bundle_id == bundle_id)
            .order_by(Card.id)
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def upsert(self, card: Card) -> Card:
        """按 id upsert:存在则更新 front/back/assets,不存在则插入。"""
        stmt = (
            insert(Card)
            .values(
                id=card.id,
                bundle_id=card.bundle_id,
                type=card.type,
                front=card.front,
                back=card.back,
                assets=card.assets,
            )
            .on_conflict_do_update(
                index_elements=["id"],
                set_={
                    "bundle_id": card.bundle_id,
                    "type": card.type,
                    "front": card.front,
                    "back": card.back,
                    "assets": card.assets,
                },
            )
            .returning(Card)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()
