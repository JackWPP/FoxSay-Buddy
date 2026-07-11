from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.domain.schemas import (
    PairingClaim,
    PairingClaimOut,
    PairingSessionCreate,
    PairingSessionOut,
)
from app.domain.services.pairing import PairingService
from app.repositories.device import DeviceRepository
from app.repositories.pairing import PairingSessionRepository

router = APIRouter(prefix="/v1/device-pairing", tags=["pairing"])


@router.post("/sessions", response_model=PairingSessionOut)
async def create_session(
    body: PairingSessionCreate,
    session: AsyncSession = Depends(get_db),
) -> PairingSessionOut:
    svc = PairingService(PairingSessionRepository(session), DeviceRepository(session))
    session_id, code, expires_at = await svc.create_session()
    await session.commit()
    return PairingSessionOut(session_id=session_id, code=code, expires_at=expires_at)


@router.post("/claim", response_model=PairingClaimOut)
async def claim(
    body: PairingClaim,
    session: AsyncSession = Depends(get_db),
) -> PairingClaimOut:
    svc = PairingService(PairingSessionRepository(session), DeviceRepository(session))
    credential = await svc.claim(body.code, body.device_id, body.firmware_version)
    await session.commit()
    return PairingClaimOut(device_id=body.device_id, credential=credential, message="device paired")
