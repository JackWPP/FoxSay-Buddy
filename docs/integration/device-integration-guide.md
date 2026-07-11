# FoxSay Buddy 嵌入式设备对接指南

**目标读者**:固件/嵌入式开发同学。本文自包含,读完即可开始写固件对接后端,不需要先通读 spec。

**后端版本**:0.1.0 ｜ **协议版本**:schema 1.0 ｜ **环境**:local(无鉴权,ADR-008)

> 后端是权威源,设备是本地优先。设备触摸动作先改本地状态写 outbox,网络恢复后异步同步。详见 [02-system-architecture.md](../specs/02-system-architecture.md)。

---

## 1. 一分钟理解

设备要做的事,本质上就 4 件:

1. **配对**:拿配对码换一个 `device_id`,登记到后端。
2. **上线**:连 MQTT,发 `presence`(retained),后端就知道你在线了。
3. **上报学习动作**:用户翻卡时,发 `study.card_action` 到 `events`,等业务 ack,ack 到了才能从本地 outbox 删这条记录。
4. **接收命令**:订阅 `commands`,收到 `content.sync` 等命令后执行,回 `message.ack`。

**所有消息共用一个 envelope**,字段固定。JSON 编码 UTF-8,字段名 snake_case,时间用 UTC RFC 3339。

---

## 2. 连接信息

### MQTT broker

| 项 | local 值 |
| --- | --- |
| Host | `localhost`(本机起服务时) |
| Port | `1883` |
| 协议 | MQTT 3.1.1 或 5 均可(payload 契约不变) |
| 鉴权 | **无**(匿名连接,ADR-008) |
| 用户名/密码 | 不需要 |
| TLS | 不需要(local) |
| Client ID | 任意,建议用 `device_id` |

> 生产环境会改为:每设备独立证书 + broker ACL(设备只能访问自身 topic)+ TLS。固件代码把"证书来源"做成可配置即可,逻辑不变。

### 后端 REST(配对 / 内容登记用)

| 项 | local 值 |
| --- | --- |
| Base URL | `http://localhost:8000` |
| OpenAPI 文档 | `http://localhost:8000/docs` |
| 鉴权 | **无** |

### 对象存储(内容包下载)

设备**不直接访问** MinIO。content.sync 命令里带一个短期签名 URL,设备用 HTTPS GET 下载。local 下 URL 形如 `http://localhost:9000/...?...`。

---

## 3. Topic 矩阵

命名空间固定 `foxsay/v1`,设备只能用自身 `{device_id}`:

| Topic | 方向 | QoS | Retain | 用途 |
| --- | --- | --- | --- | --- |
| `foxsay/v1/devices/{id}/presence` | 设备→服务端 | 1 | **yes** | 在线状态快照 + LWT 写 offline |
| `foxsay/v1/devices/{id}/events` | 设备→服务端 | 1 | no | 学习/诊断事件 |
| `foxsay/v1/devices/{id}/commands` | 服务端→设备 | 1 | no | content.sync 等命令 |
| `foxsay/v1/devices/{id}/acks` | 双向 | 1 | no | 对 events/commands 的业务确认 |

**关键约束**:
- 设备订阅自己的 `commands` 和 `acks`。local 不限制 topic,但固件**不要**订阅其他设备或 wildcard,生产环境会被 ACL 拒绝。
- presence 用 retain:设备上线发一条,后端新订阅时立即拿到当前状态;LWT 设为 `online:false` 的 presence,broker 在设备异常断开时自动发。
- events **不** retain:事件是历史记录,重发靠 `message_id` 幂等,不靠 retain。

---

## 4. 消息 envelope

所有消息共用此结构。完整 JSON Schema 在 `schemas/envelope.json`。

```json
{
  "schema_version": "1.0",
  "message_id": "01JZQY7SZP7M8M2KPF4S9F1T4J",
  "device_id": "dev_01JZQXABCD",
  "sent_at": "2026-07-11T05:30:00Z",
  "clock_synced": true,
  "device_sequence": 184,
  "type": "study.card_action",
  "payload": {}
}
```

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `schema_version` | 是 | 固定 `"1.0"`,不匹配服务端拒绝 |
| `message_id` | 是 | 全局唯一、不可推测(ULID/UUID)。**幂等键**,重发用同一个 |
| `device_id` | 是 | 配对时获得的设备 ID |
| `sent_at` | 是 | UTC RFC 3339。无墙钟时填 `null` |
| `clock_synced` | 否 | 墙钟是否已同步。false 时服务端用 `received_at` |
| `device_sequence` | 否 | 设备单调递增序号,无墙钟时辅助排序 |
| `type` | 是 | 消息类型,见下表 |
| `payload` | 是 | 按 type 解释,见 §5 |

`type` 取值:`device.presence` / `study.card_action` / `content.sync` / `device.config_update` / `device.reboot` / `ota.install` / `message.ack`。

**忽略未知字段**:服务端和设备都必须忽略 envelope / payload 里的未知可选字段(向前兼容)。但 envelope 顶层字段必须齐全,否则拒绝。

---

## 5. 各消息 payload

### 5.1 presence(设备→服务端)

```json
{
  "schema_version": "1.0",
  "message_id": "01JZQY8AABCD",
  "device_id": "dev_01JZQXABCD",
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

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `online` | 是 | 是否在线 |
| `firmware_version` | 是 | 固件版本 |
| `content_version` | 是 | 当前 active 内容包版本 |
| `network` | 否 | `wifi` / `ethernet` / `none` |
| `posture` | 否 | `upright` / `flat` / `moving` / `unknown` |
| `free_heap_bytes` | 否 | 可用堆 |
| `reset_reason` | 否 | 重启原因 |

> **不要上报 battery**。原型板是否可读电池是 TBD,确认硬件支持后再加。

**LWT(遗嘱)**:连接时设置 LWT 为 `online:false` 的 presence payload,broker 在设备异常断开时自动发布。设备正常下线前也应主动发一条 `online:false`。

### 5.2 study.card_action(设备→服务端)

```json
{
  "schema_version": "1.0",
  "message_id": "01JZQY9BCDEF",
  "device_id": "dev_01JZQXABCD",
  "sent_at": "2026-07-11T05:31:12Z",
  "clock_synced": true,
  "type": "study.card_action",
  "payload": {
    "session_id": "ses_01JZQX",
    "bundle_version": "2026.07.11.1",
    "card_id": "card_euler_identity",
    "card_type": "formula",
    "action": "mark_difficult",
    "device_sequence": 184
  }
}
```

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `session_id` | 是 | 本轮学习 session ID |
| `bundle_version` | 是 | 内容包版本 |
| `card_id` | 是 | 卡片 ID |
| `card_type` | 是 | `vocabulary` / `formula` / `wiki` |
| `action` | 是 | P0 允许:`view_next` / `flip` / `mark_difficult` / `skip` / `session_complete` |
| `device_sequence` | 否 | 设备序号 |

**幂等保证**:服务端按 `message_id` 去重。同一 `message_id` 重投,服务端返回**相同的 ack**,不重复更新统计。所以设备重发同一事件是安全的。

### 5.3 content.sync(服务端→设备)

```json
{
  "schema_version": "1.0",
  "message_id": "01JZR0CMD001",
  "device_id": "dev_01JZQXABCD",
  "sent_at": "2026-07-11T05:35:00Z",
  "expires_at": "2026-07-11T06:35:00Z",
  "type": "content.sync",
  "payload": {
    "bundle_version": "2026.07.11.2",
    "url": "http://localhost:9000/foxsay-content/...?X-Amz-Signature=...",
    "size_bytes": 2457600,
    "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  }
}
```

设备处理流程:
1. 校验 `expires_at` 未过期、`schema_version` 匹配。
2. HTTPS GET `url` 到临时文件,**逐块校验**(不要下完再算)。
3. 算 SHA-256,与 `sha256` 比对。
4. 校验通过 → 原子替换 active pointer(写新指针文件,不删旧包)。
5. 回 `message.ack`(status=succeeded)。
6. 失败(checksum 不符 / 下载失败 / 空间不足)→ 回 `message.ack`(status=failed, error_code 见 §7),**保留旧版本继续可用**。

### 5.4 message.ack(双向)

设备对收到的 command 回 ack,服务端对收到的 event 回 ack:

```json
{
  "schema_version": "1.0",
  "message_id": "01JZS0ACK001",
  "device_id": "dev_01JZQXABCD",
  "sent_at": "2026-07-11T05:35:04Z",
  "type": "message.ack",
  "payload": {
    "correlation_id": "01JZR0CMD001",
    "status": "succeeded",
    "error_code": null,
    "detail": null
  }
}
```

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `correlation_id` | 是 | 被确认消息的 `message_id` |
| `status` | 是 | `accepted` / `succeeded` / `rejected` / `failed` |
| `error_code` | 否 | 失败时的稳定机器码,见 §7 |
| `detail` | 否 | 诊断文本,**不得含秘密** |

`status` 语义:
- `accepted`:耗时命令先回这个,表示已开始处理(如大内容下载开始)。
- `succeeded`:终态,成功。
- `rejected`:终态,命令无效(过期/不支持/格式错),**不自动重试**。
- `failed`:终态,执行失败。仅当 `error_code` 明确可重试时服务端才重发。

---

## 6. 完整对接时序

### 6.1 配对(首次)

```
手机/装机工具                 后端 REST                     设备
    |                          |                           |
    |-- POST /v1/device-pairing/sessions -->|              |
    |<-- 200 {session_id, code, expires_at}              |
    |                          |                          |
    |------- 把 code 给设备(扫码/输入) -------------->|
    |                          |                          |
    |                          |<-- POST /v1/device-pairing/claim
    |                          |      {code, device_id, firmware_version}
    |                          |-- 200 {device_id, credential} -->|
    |                          |                          |
    |                          |   (设备持久化 device_id)   |
```

> local 环境配对码 TTL 600 秒,6 位数字。固件不需要真实校验 `credential`(ADR-008 占位),但要持久化 `device_id` 用于后续 MQTT。

配对也可以**跳过**:设备直接用一个固定 `device_id` 连 MQTT、发 presence,后端会自动登记未知设备(local 模式)。但建议走正规配对流程,生产环境会强制。

### 6.2 上线 + 上报事件 + 收 ack

```
设备                           broker                    后端
 |-- connect (LWT=online:false) -->|                      |
 |-- subscribe commands, acks ---->|                      |
 |-- pub presence (retain) ------->|-- 转发 ------------->| (落 last_seen)
 |                                 |                      |
 |-- pub study.card_action (QoS1)->|-- 转发 ------------->| (幂等入库 + 投影)
 |                                 |<-- pub message.ack --| (succeeded)
 |<-- message.ack (correlation=..)|                      |
 |                                 |                      |
 | (从 outbox 删这条)              |                      |
```

**重点**:MQTT 的 PUBACK 只表示"broker 收到了",**不能**替代业务 ack。设备必须等业务 `message.ack`(correlation_id = 事件 message_id,status=succeeded)才能从 outbox 删除记录。没收到 ack 就指数退避重发(用**同一个** message_id)。

### 6.3 接收命令 + 回 ack

```
后端(REST 触发)              broker                    设备
 |-- pub content.sync (QoS1) --->|-- 转发 ------------->|
 |                                |                      | (下载+校验+原子切换)
 |                                |<-- pub message.ack --| (succeeded/failed)
 |<-- message.ack ---------------|                      |
 |  (命令状态推进到终态)          |                      |
```

### 6.4 断网恢复

- 设备 outbox 是**追加式 + CRC + 容量上限**(默认 1 MiB 或 10000 事件)。
- 断网期间用户动作照常写 outbox,UI 不阻塞(optimistic feedback)。
- 恢复后按顺序重发未 ack 的事件,**用原 message_id**,服务端自动去重。
- 不要在网络恢复瞬间重发全部:用指数退避 + 抖动(见 `FW-NET-01`)。

---

## 7. 错误码

`message.ack` 的 `error_code` 用以下稳定机器码:

| error_code | 含义 | 设备动作 |
| --- | --- | --- |
| `expired` | 命令已过期 | 不重试,丢弃 |
| `unsupported_schema` | schema_version 不匹配 | 不重试,需升级固件 |
| `unsupported_command` | 未知命令类型 | 不重试 |
| `invalid_payload` | payload 格式错误 | 不重试,检查构造逻辑 |
| `busy` | 设备正忙 | 可重试 |
| `download_failed` | 下载失败 | 可重试 |
| `checksum_mismatch` | SHA-256 不符 | 可重试(重新下载) |
| `insufficient_storage` | 存储不足 | 不重试,需清理 |
| `internal_error` | 服务端内部错 | 可重试 |

**原则**:`rejected` 不重试;`failed` 仅在 error_code 明确可重试时重试。

---

## 8. outbox 与可靠性规则

固件侧必须遵守(对应 `FW-DATA-01/02/03`):

- outbox 追加式,带 CRC,ack 后回收;断电后能恢复。
- 容量达 80% 记录告警;满时优先保留学习变更,UI 提示"同步受阻"。
- 内容包下载到临时文件,哈希校验通过后**原子写 active pointer**,断电能在新旧版本里选最后完整版。
- 命令重投去重:最近处理的 command `message_id` 有界持久化(如最近 100 条),重投不重复执行(`FW-NET-04`)。

---

## 9. 参考实现:mock_device.py

后端仓库 `backend/tools/mock_device.py` 是一个可运行的 Python 模拟设备,演示全部对接行为。固件可以照着实现:

```bash
cd backend

# 1. 配对(拿 device_id)
uv run python tools/mock_device.py pair --base-url http://localhost:8000

# 2. 上线 + 上报 3 个事件 + 收 ack + 收命令
uv run python tools/mock_device.py run --device-id dev_xxx --events 3

# 3. 断网重发幂等测试(同一 message_id 发两次,验证不重复计数)
uv run python tools/mock_device.py replay --device-id dev_xxx
```

源码读 `backend/tools/mock_device.py` 的 `cmd_run` / `cmd_replay`,envelope 构造在 `make_envelope()`。这是最直接的"照着抄"参考。

---

## 10. 验证你的固件

起本地环境(需要 Docker):

```bash
# 起基础设施
sudo docker compose -f infra/compose/docker-compose.yml --env-file infra/compose/.env up -d

# 起后端
cd backend && uv run uvicorn app.main:app --reload

# 健康检查
curl http://localhost:8000/health/ready   # {"status":"ready","db":true,"mqtt":true}
```

固件连上 broker 后,用 `mosquitto_sub` 观察你的消息:

```bash
sudo docker exec foxsay-mosquitto mosquitto_sub -t 'foxsay/v1/devices/#' -v
```

用 REST 查你上报的事件,确认落库:

```bash
curl "http://localhost:8000/v1/study-events?device_id=dev_xxx"
```

---

## 11. 已知限制(对接时须知)

1. **离线命令**:服务端用 outbox worker 重试未确认命令(未到 `expires_at` 的 `pending`/`accepted` 命令每 30 秒重发一次,过期标 `expired`)。设备侧要开持久会话(`clean_session=false` + 固定 client_id),这样设备离线期间服务端发的命令在重连后由 broker 补发。命令 `message_id` 不变,设备按 `FW-NET-04` 去重,重投不重复执行。
2. **内容生产流程**:bundle 登记时若不提供 `object_key`,后端返回 `upload_url`(预签名 PUT URL,30 分钟有效),内容生产者直接 PUT 上传内容包到 MinIO,再调 `POST /v1/content-bundles/{id}/ready` 置 ready。只有 ready 的 bundle 才能 content.sync。详见后端 OpenAPI 文档。
3. **无鉴权**:local 全开放,生产前会加证书 + ACL,固件把证书来源做成可配置。
4. **payload 上限 16 KiB**:内容和资源只传 URL,不塞进 MQTT。

---

## 12. 相关文档

- 完整契约定义:[../specs/04-api-mqtt-contract.md](../specs/04-api-mqtt-contract.md)
- JSON Schema(机器可读):[`schemas/`](../../schemas/)
- 固件行为规范:[../specs/03-device-firmware-spec.md](../specs/03-device-firmware-spec.md)
- 后端架构:[../specs/02-system-architecture.md](../specs/02-system-architecture.md)
- 配对流程与 REST:[本文 §5.1 / §6.1](#51-presence设备服务端) + `http://localhost:8000/docs`

遇到契约不清楚的地方,**先看 `schemas/*.json`**,它是唯一权威。
