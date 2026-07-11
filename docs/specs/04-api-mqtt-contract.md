# 04 — API 与 MQTT 契约

**状态：Accepted（字段可在 schema 实装时细化，不改变语义）**

## 1. 通用约定

- MQTT namespace：`foxsay/v1`；
- JSON 编码 UTF-8，字段名 snake_case；
- 时间使用 UTC RFC 3339，例如 `2026-07-11T05:30:00Z`；
- 所有消息都有唯一 `message_id`；
- 服务端和设备都必须忽略未知的可选字段；
- 非兼容字段/语义变更使用新的 namespace major version；
- JSON Schema 是实现期唯一机器可读契约，存放在 `schemas/`。

## 2. 消息 envelope

```json
{
  "schema_version": "1.0",
  "message_id": "01JZQY7SZP7M8M2KPF4S9F1T4J",
  "device_id": "dev_01JZQX...",
  "sent_at": "2026-07-11T05:30:00Z",
  "type": "study.card_action",
  "payload": {}
}
```

无法获得可信墙钟时，设备发送 `sent_at: null`、`clock_synced: false` 和单调递增 `device_sequence`。服务端永远补充 `received_at`。

## 3. Topic 矩阵

| Topic | 方向 | QoS | Retain | 说明 |
| --- | --- | --- | --- | --- |
| `foxsay/v1/devices/{id}/presence` | device → server | 1 | yes | 在线/离线、版本、姿态和摘要；LWT 写 offline |
| `foxsay/v1/devices/{id}/events` | device → server | 1 | no | 学习、诊断和业务事件 |
| `foxsay/v1/devices/{id}/commands` | server → device | 1 | no | 内容同步、配置和 OTA 命令 |
| `foxsay/v1/devices/{id}/acks` | 双向 | 1 | no | 对 events/commands 的业务确认 |

ACL 要求设备 `{id}` 与证书身份一致。禁止订阅其他设备或 wildcard topic。local 环境按 ADR-008 不启用 ACL（匿名 + 全开放），生产部署必须恢复上述限制。

## 4. Presence

```json
{
  "schema_version": "1.0",
  "message_id": "01JZQ...",
  "device_id": "dev_01JZ...",
  "sent_at": "2026-07-11T05:30:00Z",
  "type": "device.presence",
  "payload": {
    "online": true,
    "firmware_version": "0.1.0",
    "content_version": "2026.07.11.1",
    "network": "wifi",
    "posture": "upright",
    "free_heap_bytes": 131072,
    "reset_reason": "power_on"
  }
}
```

不要上报原设计中的虚假 `battery`：原型板是否具有可读取电池与充电状态是 `TBD`。确认硬件支持后再增加可选字段。

## 5. 学习事件

```json
{
  "schema_version": "1.0",
  "message_id": "01JZQ...",
  "device_id": "dev_01JZ...",
  "sent_at": "2026-07-11T05:31:12Z",
  "type": "study.card_action",
  "payload": {
    "session_id": "ses_01JZ...",
    "bundle_version": "2026.07.11.1",
    "card_id": "card_euler_identity",
    "card_type": "formula",
    "action": "mark_difficult",
    "device_sequence": 184
  }
}
```

允许的 P0 action：`view_next`、`flip`、`mark_difficult`、`skip`、`session_complete`。服务端对同一 `message_id` 重投返回相同 ack，不重复更新统计。

## 6. Command

```json
{
  "schema_version": "1.0",
  "message_id": "01JZR...",
  "device_id": "dev_01JZ...",
  "sent_at": "2026-07-11T05:35:00Z",
  "expires_at": "2026-07-11T06:35:00Z",
  "type": "content.sync",
  "payload": {
    "bundle_version": "2026.07.11.2",
    "url": "https://objects.example/...signed...",
    "size_bytes": 2457600,
    "sha256": "<64 lowercase hex chars>"
  }
}
```

P0 command：

- `content.sync`：下载并原子切换内容；
- `device.config_update`：更新白名单内的非秘密配置；
- `device.reboot`：仅在安全状态重启；
- `ota.install`：安装符合版本策略和签名要求的固件。

## 7. 业务 ack

```json
{
  "schema_version": "1.0",
  "message_id": "01JZS_ACK...",
  "device_id": "dev_01JZ...",
  "sent_at": "2026-07-11T05:35:04Z",
  "type": "message.ack",
  "payload": {
    "correlation_id": "01JZR...",
    "status": "succeeded",
    "error_code": null,
    "detail": null
  }
}
```

状态为 `accepted`、`succeeded`、`rejected` 或 `failed`。耗时命令先回 `accepted`，完成后再回终态。`error_code` 是稳定机器码，`detail` 仅用于诊断且不得含秘密。

建议错误码：`expired`、`unsupported_schema`、`unsupported_command`、`invalid_payload`、`busy`、`download_failed`、`checksum_mismatch`、`insufficient_storage`、`internal_error`。

## 8. REST API（P0）

| Method & path | 用途 |
| --- | --- |
| `POST /v1/device-pairing/sessions` | 创建短期配对会话（local 无鉴权，见 §10） |
| `POST /v1/device-pairing/claim` | 设备以配对码换取绑定与设备凭据 |
| `POST /v1/devices/{id}/credentials/rotate` | 轮换或恢复设备凭据 |
| `GET /v1/devices/{id}` | 查询设备、在线和版本状态 |
| `POST /v1/content-bundles` | 创建/登记 immutable bundle |
| `POST /v1/devices/{id}/content-sync` | 下发内容同步命令 |
| `GET /v1/study-events` | 按设备/卡片/时间查询事件 |
| `GET /health/live` | 进程存活，不检查下游 |
| `GET /health/ready` | 数据库、broker 等关键依赖就绪 |

设备下载内容/OTA 使用短期 signed URL，不通过 MQTT 携带二进制。P1 语音接口建议为 `POST /v1/devices/{id}/voice-sessions` 和分段上传 URL；先定义隐私策略再实现。

## 9. 重试与过期

- 设备 event 未收到业务 ack 时指数退避重发，直到 ack 或本地保留策略触发；
- 服务端 command 最多按策略重发，`expires_at` 后标为 expired；
- `rejected` 不自动重试；`failed` 仅在错误码明确可重试时重试；
- ack 也可能重复，双方按 `correlation_id + status` 幂等处理；
- presence 是快照，可被新值覆盖；events 不 retain。

## 10. 鉴权（local 环境）

ADR-008 决定 MVP 不做任何鉴权。local 环境具体表现为：

- broker：`allow_anonymous true`，不配置 ACL，任何客户端可连、可订阅任意 topic；
- REST：所有端点无 token / 无 API key，直接开放；
- 设备配对：`POST /v1/device-pairing/sessions` 无需身份即可创建配对码，`claim` 换取的设备凭据仅为占位标识，不做强制校验；
- 仅靠网络隔离保证安全，部署在可信网络或本机。

生产部署必须在试产前恢复：每设备独立凭据、broker ACL（设备只能访问自身 topic）、REST 鉴权与 TLS。
