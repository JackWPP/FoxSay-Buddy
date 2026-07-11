from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.domain.schemas import ContentBundleCreate, ContentBundleOut
from app.domain.services.content import ContentService
from app.repositories.command import DeviceCommandRepository
from app.repositories.content_bundle import ContentBundleRepository

router = APIRouter(prefix="/v1/content-bundles", tags=["content"])


@router.post("", response_model=ContentBundleOut)
async def create_bundle(
    body: ContentBundleCreate,
    session: AsyncSession = Depends(get_db),
) -> ContentBundleOut:
    svc = ContentService(ContentBundleRepository(session), DeviceCommandRepository(session))
    bundle = await svc.register_bundle(
        body.version, body.manifest_url, body.sha256, body.size_bytes, body.object_key
    )
    await session.commit()
    return ContentBundleOut(
        id=bundle.id,
        version=bundle.version,
        sha256=bundle.sha256,
        size_bytes=bundle.size_bytes,
        status=bundle.status,
        created_at=bundle.created_at,
    )


@router.get("", response_model=list[ContentBundleOut])
async def list_bundles(
    limit: int = 100,
    session: AsyncSession = Depends(get_db),
) -> list[ContentBundleOut]:
    repo = ContentBundleRepository(session)
    bundles = await repo.list_all(limit=limit)
    return [
        ContentBundleOut(
            id=b.id,
            version=b.version,
            sha256=b.sha256,
            size_bytes=b.size_bytes,
            status=b.status,
            created_at=b.created_at,
        )
        for b in bundles
    ]
