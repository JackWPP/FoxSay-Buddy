# infra - 本地开发基础设施

`docker compose` 一键起 FoxSay 后端依赖的全部基础设施。版本固定（非 `latest`），见 `docker-compose.yml` 顶部用法。

## 服务

| 服务 | 端口 | 说明 |
| --- | --- | --- |
| PostgreSQL 16 | `5432` | 设备/内容/学习事件/命令 |
| Mosquitto 2.0 | `1883` (MQTT) / `9001` (WS) | 匿名连接（ADR-008），无 ACL |
| MinIO | `9000` (S3) / `9001` (console) | 内容包 / OTA 对象存储 |

## 起服务

```bash
cp infra/compose/.env.example infra/compose/.env     # 一次性
docker compose -f infra/compose/docker-compose.yml --env-file infra/compose/.env up -d
```

后端用 uv 热重载，不进 compose：

```bash
uv run uvicorn app.main:app --reload
```

一键起全栈（含 backend 容器）：

```bash
docker compose -f infra/compose/docker-compose.yml --profile full up -d --build
```

## 连接信息

| 项 | 值（local） |
| --- | --- |
| `DATABASE_URL` | `postgresql+asyncpg://foxsay:foxsay_dev@localhost:5432/foxsay` |
| MQTT broker | `localhost:1883`（匿名，任意 topic 可读写） |
| S3 endpoint | `http://localhost:9000`（key=foxsay / secret=foxsay_dev_password） |
| MinIO console | http://localhost:9001 |
| Bucket | `foxsay-content`（后端启动时自动创建） |

## 安全说明

当前为 `local` 环境：**无鉴权、无 ACL、无 TLS**（ADR-008）。仅靠网络隔离，部署在可信网络或本机。`staging/production` 必须恢复每设备凭据、broker ACL（见 `mosquitto/acl.conf`）与 TLS。
