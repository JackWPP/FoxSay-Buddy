"""内容领域服务：bundle 登记与 content.sync 命令构建（含 MinIO 预签名 URL）。"""

import asyncio
from datetime import UTC, datetime, timedelta

from minio.error import S3Error
from ulid import ULID

from app.core.config import settings
from app.core.errors import AppError, ErrorCode
from app.core.logging import get_logger
from app.domain.models import ContentBundle, DeviceCommand
from app.domain.schemas import ContentSyncPayload
from app.repositories.command import DeviceCommandRepository
from app.repositories.content_bundle import ContentBundleRepository

log = get_logger("app.domain.content")

SYNC_URL_TTL = timedelta(hours=1)
UPLOAD_URL_TTL = timedelta(minutes=30)
BUNDLE_KEY_PREFIX = "bundles/"


class ContentService:
    def __init__(
        self,
        bundle_repo: ContentBundleRepository,
        command_repo: DeviceCommandRepository,
        minio_client=None,
    ) -> None:
        self.bundle_repo = bundle_repo
        self.command_repo = command_repo
        self.minio = minio_client

    async def register_bundle(
        self,
        version: str,
        manifest_url: str | None,
        sha256: str,
        size_bytes: int,
        object_key: str | None = None,
    ) -> tuple[ContentBundle, str | None]:
        """登记 bundle。返回 (bundle, upload_url)。

        - 若调用方已知 object_key（内容已在 MinIO），status=ready，无 upload_url。
        - 否则后端生成 object_key + 预签名 PUT URL，status=created；
          调用方 PUT 上传后调 mark_ready 置 ready。
        """
        existing = await self.bundle_repo.get_by_version(version)
        if existing is not None:
            raise AppError(ErrorCode.CONFLICT, f"bundle version {version} already exists", 409)

        upload_url: str | None = None
        if object_key is None:
            object_key = f"{BUNDLE_KEY_PREFIX}{version}.bundle"
        # 无 minio 或已有 manifest_url 视为外部托管，直接 ready
        status = "ready" if (manifest_url and not self.minio) or self.minio is None else "created"

        bundle = ContentBundle(
            id=f"cb_{ULID()}",
            version=version,
            object_key=object_key,
            manifest_url=manifest_url or "",
            sha256=sha256,
            size_bytes=size_bytes,
            status=status,
        )
        bundle = await self.bundle_repo.create(bundle)

        if status == "created" and self.minio is not None:
            upload_url = await asyncio.to_thread(self._presigned_put, object_key)

        log.info(
            "bundle_registered",
            bundle_id=bundle.id,
            version=version,
            status=status,
            has_upload_url=upload_url is not None,
        )
        return bundle, upload_url

    async def mark_ready(self, bundle_id: str) -> ContentBundle:
        """内容生产者上传完成后确认 bundle 可用。"""
        bundle = await self.bundle_repo.get(bundle_id)
        if bundle is None:
            raise AppError(ErrorCode.NOT_FOUND, f"bundle {bundle_id} not found", 404)
        if bundle.status == "ready":
            return bundle
        # TODO: 可选校验 MinIO 中 object 是否存在 + 大小匹配
        await self.bundle_repo.update_status(bundle_id, "ready")
        bundle.status = "ready"
        log.info("bundle_ready", bundle_id=bundle_id, version=bundle.version)
        return bundle

    def _presigned_put(self, object_key: str) -> str:
        if self.minio is None:
            return ""
        try:
            return self.minio.presigned_put_object(
                settings.s3_bucket, object_key, expires=UPLOAD_URL_TTL
            )
        except S3Error as e:
            log.error("presign_put_failed", object_key=object_key, error=str(e))
            raise AppError(ErrorCode.INTERNAL_ERROR, "failed to create upload url", 500) from e

    def _presigned_get(self, object_key: str) -> str:
        if self.minio is None or not object_key:
            return ""
        try:
            return self.minio.presigned_get_object(
                settings.s3_bucket, object_key, expires=SYNC_URL_TTL
            )
        except S3Error as e:
            log.error("presign_failed", object_key=object_key, error=str(e))
            return ""

    async def build_content_sync(
        self,
        device_id: str,
        bundle_version: str,
    ) -> tuple[DeviceCommand, ContentSyncPayload]:
        bundle = await self.bundle_repo.get_by_version(bundle_version)
        if bundle is None:
            raise AppError(ErrorCode.NOT_FOUND, f"bundle {bundle_version} not found", 404)

        url = (
            await asyncio.to_thread(self._presigned_get, bundle.object_key)
            if bundle.object_key
            else (bundle.manifest_url or "")
        )
        payload = ContentSyncPayload(
            bundle_version=bundle.version,
            url=url,
            size_bytes=bundle.size_bytes,
            sha256=bundle.sha256,
        )
        command = DeviceCommand(
            message_id=f"cmd_{ULID()}",
            device_id=device_id,
            type="content.sync",
            payload=payload.model_dump(),
            expires_at=datetime.now(UTC) + SYNC_URL_TTL,
            status="pending",  # outbox worker 负责确保送达;成功 publish 后变 accepted
        )
        await self.command_repo.create(command)
        log.info(
            "content_sync_command_created",
            device_id=device_id,
            bundle_version=bundle_version,
            command_id=command.message_id,
        )
        return command, payload
