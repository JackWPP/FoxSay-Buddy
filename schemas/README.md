# Schemas - 跨端契约

FoxSay v1 消息的**唯一机器可读契约**。固件、后端和测试共同引用本目录，协议变更必须先改这里。

## 消息类型

| 文件 | type | topic | 方向 |
| --- | --- | --- | --- |
| `envelope.json` | （通用信封） | — | 所有消息共用 |
| `presence.json` | `device.presence` | `foxsay/v1/devices/{id}/presence` (retained) | device → server |
| `study_event.json` | `study.card_action` | `foxsay/v1/devices/{id}/events` | device → server |
| `command.json` | `content.sync` / `device.config_update` / `device.reboot` / `ota.install` | `foxsay/v1/devices/{id}/commands` | server → device |
| `ack.json` | `message.ack` | `foxsay/v1/devices/{id}/acks` | 双向 |

字段语义见 [`docs/specs/04-api-mqtt-contract.md`](../docs/specs/04-api-mqtt-contract.md)。

## fixtures

`fixtures/*_valid.json` 必须通过对应 schema；`fixtures/*_invalid*.json` 必须被拒绝。契约测试按文件名约定自动加载。

## 规则

- JSON Schema 2020-12，UTF-8，snake_case。
- envelope 层 `additionalProperties: false`（顶层字段严格）；payload 层 `additionalProperties: true`（容忍并忽略未知可选字段）。
- `sent_at` 允许 null（设备无墙钟时）；`clock_synced` / `device_sequence` 可选。
- 非兼容变更：提升 `schema_version` major 并切换 namespace `foxsay/v2`。
