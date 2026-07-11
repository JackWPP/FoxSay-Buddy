from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.domain.schemas import StudyEventOut
from app.repositories.study_event import StudyEventRepository

router = APIRouter(prefix="/v1/study-events", tags=["study"])


@router.get("", response_model=list[StudyEventOut])
async def list_events(
    device_id: str,
    card_id: str | None = None,
    limit: int = 100,
    session: AsyncSession = Depends(get_db),
) -> list[StudyEventOut]:
    repo = StudyEventRepository(session)
    events = await repo.list_by_device(device_id, limit=limit, card_id=card_id)
    return [
        StudyEventOut(
            message_id=e.message_id,
            device_id=e.device_id,
            card_id=e.card_id,
            action=e.action,
            occurred_at=e.occurred_at,
            received_at=e.received_at,
        )
        for e in events
    ]
