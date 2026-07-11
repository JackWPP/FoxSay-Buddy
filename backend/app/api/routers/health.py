from fastapi import APIRouter, Request
from sqlalchemy import text

router = APIRouter(tags=["health"])


@router.get("/health/live")
async def live() -> dict:
    """进程存活，不检查下游。"""
    return {"status": "alive"}


@router.get("/health/ready")
async def ready(request: Request) -> dict:
    """数据库与 broker 就绪检查。"""
    db_ok = False
    try:
        async with request.app.state.async_session() as session:
            await session.execute(text("SELECT 1"))
        db_ok = True
    except Exception:  # noqa: BLE001
        db_ok = False

    mqtt_ok = getattr(request.app.state.mqtt_bridge, "connected", False)

    ready_ok = db_ok and mqtt_ok
    return {"status": "ready" if ready_ok else "not_ready", "db": db_ok, "mqtt": mqtt_ok}
