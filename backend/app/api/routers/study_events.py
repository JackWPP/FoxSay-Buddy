from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.domain.schemas import CardProgressOut, Page, StudyEventOut
from app.repositories.study_event import StudyEventRepository

router = APIRouter(prefix="/v1/study-events", tags=["study"])


@router.get("", response_model=Page[StudyEventOut])
async def list_events(
    device_id: str,
    card_id: str | None = None,
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_db),
) -> Page[StudyEventOut]:
    repo = StudyEventRepository(session)
    # 同一 async session 不支持并发查询，顺序执行
    events = await repo.list_by_device(
        device_id, limit=limit, offset=offset, card_id=card_id
    )
    total = await repo.count_by_device(device_id, card_id=card_id)
    return Page(
        items=[
            StudyEventOut(
                message_id=e.message_id,
                device_id=e.device_id,
                card_id=e.card_id,
                action=e.action,
                occurred_at=e.occurred_at,
                received_at=e.received_at,
            )
            for e in events
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/progress/{device_id}", response_model=list[CardProgressOut])
async def list_progress(
    device_id: str,
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_db),
) -> list[CardProgressOut]:
    repo = StudyEventRepository(session)
    rows = await repo.list_progress(device_id, limit=limit, offset=offset)
    return [
        CardProgressOut(
            device_id=r.device_id,
            card_id=r.card_id,
            difficulty=r.difficulty,
            last_seen_at=r.last_seen_at,
            revision=r.revision,
        )
        for r in rows
    ]
