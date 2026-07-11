import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from minio import Minio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.mqtt.bridge import MQTTBridge

log = get_logger("app.lifespan")

engine = create_async_engine(settings.database_url, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


def _ensure_bucket(client: Minio, bucket: str) -> None:
    try:
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)
        log.info("minio_bucket_ready", bucket=bucket)
    except Exception as e:  # noqa: BLE001
        # 不阻断启动：内容下发功能会降级，但 MQTT/DB 路径仍可用
        log.error("minio_bucket_init_failed", bucket=bucket, error=str(e))


@asynccontextmanager
async def lifespan(app) -> AsyncIterator[None]:
    configure_logging(settings.log_level)
    log.info("startup", environment=settings.environment)

    minio_client = Minio(
        settings.s3_host,
        access_key=settings.s3_access_key,
        secret_key=settings.s3_secret_key,
        secure=settings.s3_secure,
    )
    await asyncio.to_thread(_ensure_bucket, minio_client, settings.s3_bucket)

    bridge = MQTTBridge(session_factory=AsyncSessionLocal)
    await bridge.start()

    app.state.mqtt_bridge = bridge
    app.state.engine = engine
    app.state.async_session = AsyncSessionLocal
    app.state.minio = minio_client

    try:
        yield
    finally:
        await bridge.stop()
        await engine.dispose()
        log.info("shutdown")
