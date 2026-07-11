# FoxSay Buddy 开发规范索引

**状态：Accepted（MVP 基线）**
**版本：0.1.0**
**更新日期：2026-07-11**

本目录把原始设计资料转换为可实施、可测试、可验收的工程契约。原始材料保留在 `foxsay_hardware_design_package/`，其中的概念若与这里冲突，以这里为准。

## 阅读顺序

| 文档 | 解决的问题 |
| --- | --- |
| [01-product-spec.md](01-product-spec.md) | 产品是谁用、MVP 做什么、不做什么、如何验收 |
| [02-system-architecture.md](02-system-architecture.md) | 组件边界、数据流、技术选型、部署与安全 |
| [03-device-firmware-spec.md](03-device-firmware-spec.md) | 固件任务、状态机、UI 手势、存储和性能预算 |
| [04-api-mqtt-contract.md](04-api-mqtt-contract.md) | REST/MQTT 契约、QoS、幂等、确认与错误语义 |
| [05-delivery-plan.md](05-delivery-plan.md) | 分阶段实施、测试矩阵、风险和完成门槛 |

## 需求标记

- `P0`：MVP 发布阻断项；
- `P1`：MVP 稳定后进入下一迭代；
- `P2`：探索项，不应影响 P0 架构与排期；
- `TBD`：必须通过真机或产品决策关闭，不能静默假设。

需求 ID 在代码、测试和 PR 中保持稳定，例如 `FW-NET-03`、`BE-MQTT-02`。

## 已确认决策

| ID | 决策 | 原因 |
| --- | --- | --- |
| ADR-001 | 单仓库管理 firmware/backend/infra/schemas | 跨端协议需要原子变更和契约测试 |
| ADR-002 | 固件使用 ESP-IDF + LVGL，后端使用 FastAPI | 符合目标板官方生态与既有方案 |
| ADR-003 | MQTT 只传状态、事件和命令，不传音频二进制 | 控制面与大数据面分离，便于限流、重试和观测 |
| ADR-004 | MVP 语音使用 HTTPS 分段上传；实时双工流列为 P1 | 先降低 NAT、丢包、鉴权和回声处理风险 |
| ADR-005 | MQTT topic 不使用开头 `/`，以 `foxsay/v1` 作为命名空间 | 避免空 topic level，并支持协议演进 |
| ADR-006 | 所有命令要求 ack，事件按 `message_id` 幂等消费 | 解决 QoS 1 重复投递与设备离线后的状态不确定性 |
| ADR-007 | MVP 先做竖切闭环，再扩展 Wiki、翻译和游戏 | 优先验证设备交互、同步与可靠性三项核心风险 |
| ADR-008 | MVP 不做任何账户体系与鉴权 | 降低对接摩擦，先打通设备交互与中台能力；主程序后续以服务方式对接，账户/凭据/ACL 留到试产前引入 |

## 待关闭问题

| ID | 问题 | 关闭时点 |
| --- | --- | --- |
| TBD-001 | 量产硬件是否就是立创·实战派 ESP32-S3，还是仅为原型板 | Phase 0 结束前 |
| TBD-002 | LCD/触控 BSP 的准确芯片、旋转方向与坐标映射 | Phase 0 真机探针 |
| TBD-003 | 是否需要账户体系 | 已关闭（2026-07-11，ADR-008）：MVP 不做账户与鉴权，数据归属挂在 Device 上 |
| TBD-004 | AI/翻译供应商、数据保留期限与未成年人隐私要求 | 语音功能进入 P0 前 |
| TBD-005 | 中文字体的目标字符集与 SD 卡是否为必需依赖 | UI vertical slice 前 |
