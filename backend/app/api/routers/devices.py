from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.errors import AppError, ErrorCode
from app.domain.schemas import DeviceOut
from app.repositories.device import DeviceRepository

router = APIRouter(prefix="/v1/devices", tags=["devices"])

STALE_SECONDS = 90


def _is_online(last_seen_at) -> bool:
    return last_seen_at is not None and (datetime.now(UTC) - last_seen_at) < timedelta(
        seconds=STALE_SECONDS
    )


@router.get("", response_model=list[DeviceOut])
async def list_devices(
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_db),
) -> list[DeviceOut]:
    repo = DeviceRepository(session)
    devices = await repo.list_all(limit=limit, offset=offset)
    return [
        DeviceOut(
            id=d.id,
            name=d.name,
            firmware_version=d.firmware_version,
            content_version=d.content_version,
            last_seen_at=d.last_seen_at,
            online=_is_online(d.last_seen_at),
        )
        for d in devices
    ]


@router.get("/{device_id}", response_model=DeviceOut)
async def get_device(
    device_id: str,
    session: AsyncSession = Depends(get_db),
) -> DeviceOut:
    repo = DeviceRepository(session)
    device = await repo.get(device_id)
    if device is None:
        raise AppError(ErrorCode.NOT_FOUND, "device not found", 404)
    return DeviceOut(
        id=device.id,
        name=device.name,
        firmware_version=device.firmware_version,
        content_version=device.content_version,
        last_seen_at=device.last_seen_at,
        online=_is_online(device.last_seen_at),
    )


@router.post("/{device_id}/credentials/rotate")
async def rotate_credentials(
    device_id: str,
    session: AsyncSession = Depends(get_db),
) -> dict:
    """ADR-008：占位实现，不实际轮换凭据。试产前补凭据轮换与 ACL。"""
    repo = DeviceRepository(session)
    device = await repo.get(device_id)
    if device is None:
        raise AppError(ErrorCode.NOT_FOUND, "device not found", 404)
    return {
        "device_id": device_id,
        "credential": "devtok_rotate_placeholder",
        "message": "credential rotation not enforced (ADR-008)",
    }
