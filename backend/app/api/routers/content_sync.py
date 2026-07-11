from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_minio, get_publisher
from app.core.errors import AppError, ErrorCode
from app.core.logging import get_logger
from app.domain.schemas import ContentSyncCommandOut, ContentSyncRequest
from app.domain.services.content import ContentService
from app.repositories.command import DeviceCommandRepository
from app.repositories.content_bundle import ContentBundleRepository
from app.repositories.device import DeviceRepository

log = get_logger("app.api.content_sync")
router = APIRouter(prefix="/v1/devices", tags=["content"])


@router.post("/{device_id}/content-sync", response_model=ContentSyncCommandOut)
async def content_sync(
    device_id: str,
    body: ContentSyncRequest,
    session: AsyncSession = Depends(get_db),
    publisher=Depends(get_publisher),
    minio_client=Depends(get_minio),
) -> ContentSyncCommandOut:
    device = await DeviceRepository(session).get(device_id)
    if device is None:
        raise AppError(ErrorCode.NOT_FOUND, "device not found", 404)

    svc = ContentService(
        ContentBundleRepository(session),
        DeviceCommandRepository(session),
        minio_client=minio_client,
    )
    command, payload = await svc.build_content_sync(device_id, body.bundle_version)
    await session.commit()

    # 通过 MQTT 下发命令。MVP 直接发；TODO: outbox worker 在断线后重发。
    try:
        await publisher.publish_command(
            device_id,
            command.message_id,
            command.type,
            payload.model_dump(),
            expires_at=command.expires_at,
        )
    except Exception as e:  # noqa: BLE001
        log.error("content_sync_publish_failed", command_id=command.message_id, error=str(e))

    return ContentSyncCommandOut(
        message_id=command.message_id,
        command_type=command.type,
        expires_at=command.expires_at,
    )
