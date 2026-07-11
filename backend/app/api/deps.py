from collections.abc import AsyncIterator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db(request: Request) -> AsyncIterator[AsyncSession]:
    async with request.app.state.async_session() as session:
        yield session


def get_publisher(request: Request):
    return request.app.state.mqtt_bridge.publisher


def get_minio(request: Request):
    return request.app.state.minio
