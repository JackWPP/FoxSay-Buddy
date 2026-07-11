from fastapi import FastAPI

from app.api.errors import register_error_handlers
from app.api.routers import (
    cards,
    content_bundles,
    content_sync,
    devices,
    health,
    pairing,
    study_events,
)
from app.core.lifespan import lifespan


def create_app() -> FastAPI:
    app = FastAPI(
        title="FoxSay Buddy Backend",
        version="0.1.0",
        description="MQTT 中台 + REST API（ADR-008：MVP 无鉴权）",
        lifespan=lifespan,
    )
    register_error_handlers(app)
    app.include_router(health.router)
    app.include_router(pairing.router)
    app.include_router(devices.router)
    app.include_router(content_bundles.router)
    app.include_router(cards.router)
    app.include_router(content_sync.router)
    app.include_router(study_events.router)
    return app


app = create_app()
