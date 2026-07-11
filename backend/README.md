# FoxSay Backend

FastAPI 服务：MQTT 中台 + REST API。权威源：账户外的设备、内容版本、学习记录与命令状态。

> 当前遵循 ADR-008：**MVP 不做鉴权**。broker 匿名连接、REST 全开放。

## 本地开发

```bash
# 1. 起基础设施（PostgreSQL + Mosquitto + MinIO）
docker compose -f infra/compose/docker-compose.yml --env-file infra/compose/.env up -d

# 2. 装依赖
uv sync

# 3. 跑 migration
uv run alembic upgrade head

# 4. 起后端（热重载）
uv run uvicorn app.main:app --reload
```

打开 http://localhost:8000/docs 看 OpenAPI，http://localhost:8000/health/ready 看依赖就绪。

## 结构

```
app/
  main.py            FastAPI app 工厂
  core/              config / logging / lifespan
  api/routers/       HTTP endpoints（无鉴权）
  domain/            ORM 实体 + Pydantic DTO + services
  repositories/       PostgreSQL 访问层
  mqtt/              bridge / router / handlers / publisher / ack_tracker
  workers/           后台任务（内容构建等）
  observability/     metrics
```

分层约定：`api` / `mqtt` 只做校验与 DTO 转换；业务规则在 `domain/services`；数据库访问集中在 `repositories`。事件消费幂等，DB 写入与后续发布用事务/outbox。

## 测试

```bash
uv run pytest
uv run ruff check .
uv run mypy app
```

契约测试验证 `schemas/` 下的 JSON Schema 与 fixtures。

## 配置

环境变量见 `infra/compose/.env.example`。本地开发时 backend 读取同目录 `.env`（由 pydantic-settings 加载）。
