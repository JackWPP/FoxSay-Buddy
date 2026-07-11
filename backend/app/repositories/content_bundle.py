from sqlalchemy import select

from app.domain.models import ContentBundle
from app.repositories.base import BaseRepository


class ContentBundleRepository(BaseRepository):
    async def get_by_version(self, version: str) -> ContentBundle | None:
        result = await self.session.execute(
            select(ContentBundle).where(ContentBundle.version == version)
        )
        return result.scalar_one_or_none()

    async def get(self, bundle_id: str) -> ContentBundle | None:
        return await self.session.get(ContentBundle, bundle_id)

    async def create(self, bundle: ContentBundle) -> ContentBundle:
        self.session.add(bundle)
        await self.session.flush()
        return bundle

    async def list_all(self, limit: int = 100) -> list[ContentBundle]:
        result = await self.session.execute(
            select(ContentBundle).order_by(ContentBundle.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())
