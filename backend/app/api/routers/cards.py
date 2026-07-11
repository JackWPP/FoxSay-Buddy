from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.domain.models import Card
from app.domain.schemas import CardCreate, CardOut
from app.repositories.card import CardRepository

router = APIRouter(prefix="/v1/cards", tags=["cards"])


@router.post("", response_model=CardOut)
async def create_card(
    body: CardCreate,
    session: AsyncSession = Depends(get_db),
) -> CardOut:
    """创建或更新卡片(upsert)。用于内容生产阶段批量登记卡片。"""
    repo = CardRepository(session)
    card = await repo.upsert(
        Card(
            id=body.id,
            bundle_id=body.bundle_id,
            type=body.type,
            front=body.front,
            back=body.back,
            assets=body.assets,
        )
    )
    await session.commit()
    return CardOut(
        id=card.id,
        bundle_id=card.bundle_id,
        type=card.type,
        front=card.front,
        back=card.back,
        assets=card.assets,
    )


@router.get("/{card_id}", response_model=CardOut)
async def get_card(
    card_id: str,
    session: AsyncSession = Depends(get_db),
) -> CardOut:
    from app.core.errors import AppError, ErrorCode

    repo = CardRepository(session)
    card = await repo.get(card_id)
    if card is None:
        raise AppError(ErrorCode.NOT_FOUND, "card not found", 404)
    return CardOut(
        id=card.id,
        bundle_id=card.bundle_id,
        type=card.type,
        front=card.front,
        back=card.back,
        assets=card.assets,
    )


@router.get("", response_model=list[CardOut])
async def list_cards(
    bundle_id: str,
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_db),
) -> list[CardOut]:
    repo = CardRepository(session)
    cards = await repo.list_by_bundle(bundle_id, limit=limit, offset=offset)
    return [
        CardOut(
            id=c.id, bundle_id=c.bundle_id, type=c.type, front=c.front, back=c.back, assets=c.assets
        )
        for c in cards
    ]
