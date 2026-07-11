"""端到端集成测试：MQTT 幂等入库 + 业务 ack + 命令下发。

需要 docker compose 栈（Postgres + Mosquitto）与运行中的后端。默认跳过：

    docker compose -f infra/compose/docker-compose.yml --env-file infra/compose/.env up -d
    uv run alembic upgrade head
    uv run uvicorn app.main:app &
    FOXSAY_INTEGRATION=1 uv run pytest tests/integration -v
"""

import os

import pytest

pytestmark = pytest.mark.skipif(
    not os.environ.get("FOXSAY_INTEGRATION"),
    reason="set FOXSAY_INTEGRATION=1 to run (needs docker compose stack + running backend)",
)


async def test_study_event_idempotent_e2e():
    """publish 两次相同 message_id -> DB 仅一条事件 + 两次 succeeded ack（设备清 outbox）。

    TODO: 用 aiomqtt 发布 + httpx 查询 /v1/study-events 断言计数不变。
    """
    pass


async def test_content_sync_command_roundtrip():
    """REST 下发 content-sync -> 设备收到命令 -> 回 ack -> 命令状态 succeeded。

    TODO: httpx POST /v1/content-bundles + /v1/devices/{id}/content-sync，
    mock_device 收命令回 ack，查 /v1/devices/{id} 或 DB 断言命令终态。
    """
    pass
