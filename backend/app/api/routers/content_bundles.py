from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_minio
from app.domain.schemas import ContentBundleCreate, ContentBundleOut
from app.domain.services.content import ContentService
from app.repositories.command import DeviceCommandRepository
from app.repositories.content_bundle import ContentBundleRepository

router = APIRouter(prefix="/v1/content-bundles", tags=["content"])


def _to_out(bundle, upload_url: str | None = None) -> ContentBundleOut:
    return ContentBundleOut(
        id=bundle.id,
        version=bundle.version,
        sha256=bundle.sha256,
        size_bytes=bundle.size_bytes,
        status=bundle.status,
        object_key=bundle.object_key,
        upload_url=upload_url,
        created_at=bundle.created_at,
    )


@router.post("", response_model=ContentBundleOut)
async def create_bundle(
    body: ContentBundleCreate,
    session: AsyncSession = Depends(get_db),
    minio_client=Depends(get_minio),
) -> ContentBundleOut:
    """登记 bundle。若 object_key 未提供，返回 upload_url 供调用方 PUT 上传内容包。
    上传完成后调 POST /v1/content-bundles/{id}/ready 置 ready。
    """
    svc = ContentService(
        ContentBundleRepository(session),
        DeviceCommandRepository(session),
        minio_client=minio_client,
    )
    bundle, upload_url = await svc.register_bundle(
        body.version, body.manifest_url, body.sha256, body.size_bytes, body.object_key
    )
    await session.commit()
    return _to_out(bundle, upload_url)


@router.post("/{bundle_id}/ready", response_model=ContentBundleOut)
async def mark_ready(
    bundle_id: str,
    session: AsyncSession = Depends(get_db),
    minio_client=Depends(get_minio),
) -> ContentBundleOut:
    """内容生产者上传完成后确认 bundle 可用。"""
    svc = ContentService(
        ContentBundleRepository(session),
        DeviceCommandRepository(session),
        minio_client=minio_client,
    )
    bundle = await svc.mark_ready(bundle_id)
    await session.commit()
    return _to_out(bundle)


@router.get("", response_model=list[ContentBundleOut])
async def list_bundles(
    limit: int = 100,
    session: AsyncSession = Depends(get_db),
) -> list[ContentBundleOut]:
    repo = ContentBundleRepository(session)
    bundles = await repo.list_all(limit=limit)
    return [_to_out(b) for b in bundles]
