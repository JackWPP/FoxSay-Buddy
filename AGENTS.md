# FoxSay Buddy 协作指南

## 1. 项目目标

FoxSay Buddy 是运行在立创·实战派 ESP32-S3（N16R8）上的桌面学习伴侣。设备通过 320×240 触摸屏、音频与姿态传感器提供闪卡、知识推送、专注提醒和语音交互；后端负责账户、内容、同步、设备管理与 AI 能力。

当前仓库处于 Spec-first 阶段。实现必须优先完成 `docs/specs/` 中的 MVP，不得把远期设想混入首版主路径。

## 2. 规范优先级

发生冲突时按以下顺序执行：

1. 用户在当前任务中的明确要求；
2. 本文件；
3. `docs/specs/` 下标记为 `Accepted` 的规范；
4. `foxsay_hardware_design_package/spec_markdown/` 下的原始设计资料；
5. UI 样机与 PDF。

原始设计资料是需求输入，不是最终实现契约。修改行为、协议或验收标准时，必须先更新对应 Spec，并在 `docs/specs/README.md` 的决策记录中说明。

## 3. 预期仓库结构

```text
firmware/                 ESP-IDF 固件
  main/                   组合层与启动入口
  components/             可复用驱动、服务、UI 与领域组件
  test/                   host/unit 与硬件测试辅助代码
backend/                  FastAPI 服务
  app/                    API、领域服务、数据访问与 MQTT bridge
  tests/                  单元、集成与契约测试
web/                      可选的管理/学习 Web 客户端（非 P0）
infra/                    Compose、Mosquitto 与本地开发配置
schemas/                  JSON Schema/OpenAPI 等跨端契约
docs/specs/               实施规范与决策记录
foxsay_hardware_design_package/  原始设计输入，只做归档
```

新增顶层目录前先判断是否属于以上边界，不创建含义重复的 `src2/`、`misc/`、`temp/` 等目录。

## 4. 工程约定

### 通用

- 文档、用户可见文本与业务说明使用简体中文；代码标识符、协议字段和提交标题使用英文。
- 时间戳统一为 UTC RFC 3339 字符串；设备内部可用 monotonic clock 计算时长。
- ID 使用不可推测的 UUID/ULID；禁止用数组下标或自增 ID 充当跨端资源标识。
- 跨端数据先改 `schemas/` 中的契约，再改生产者和消费者；协议变更必须向后兼容或提升 `schema_version`。
- 不提交密钥、真实 Wi-Fi、设备证书、录音、个人学习数据或生产日志。
- 避免无关重构。保留用户已有修改，不覆盖未知来源的工作区变更。

### 固件

- 使用 ESP-IDF 原生组件模型；提交 `sdkconfig.defaults`，不提交机器生成的 `sdkconfig`。
- BSP/驱动、领域逻辑和 LVGL 页面分层，页面不得直接操作 MQTT、NVS 或硬件驱动。
- LVGL 只在 UI task 中调用；跨 task 更新通过队列/事件传递。
- 网络、音频、SD 卡操作不得阻塞 UI task。热路径避免无界动态分配和大对象复制。
- 所有设备命令都必须可重复执行，或通过 `message_id` 去重；离线动作先进入有上限的本地 outbox。
- 新增资源时记录 Flash、PSRAM、内部 RAM 与 SD 卡预算；不得把完整中文字库或大体积动画直接编入 app image。
- 硬件相关代码必须提供超时与可诊断错误，不能无限等待外设。

### 后端

- API 层只做鉴权、校验与 DTO 转换；业务规则放 service/domain 层；数据库访问集中在 repository 层。
- MQTT handler 先校验 topic、payload、设备身份和 schema，再进入领域服务。
- 消费事件必须幂等；数据库状态更新与后续发布使用事务/outbox，避免“已写库但未回复”。
- 所有外部 I/O 设置显式超时；重试只用于幂等操作，并采用指数退避与抖动。
- 日志使用结构化字段，至少包含 `request_id`、`device_id` 或 `message_id`；不得记录 token 与原始语音。

## 5. 测试与验证

实现代码出现后，以各子项目 README 中的命令为准。每次变更至少完成与影响范围相符的检查：

- 文档：链接可达、Mermaid/JSON 示例语法正确、术语与协议一致；
- 固件：format、静态检查、目标板编译；涉及状态机或解析器时运行 host/unit tests；
- 后端：format、lint、type check、unit tests；涉及数据库/MQTT 时运行集成与契约测试；
- 协议：用同一份 schema 验证示例、固件 fixture 和后端 fixture；
- UI/硬件：在真机验证触控方向、最低字号、帧率、断网恢复和休眠唤醒。

不能运行某项验证时，在交付说明中明确写出未验证项、原因与风险，不用“理论上可行”代替结果。

## 6. Definition of Done

一项功能只有同时满足以下条件才算完成：

- 对应 Spec 和验收标准已更新；
- 正常、错误、超时、断网/重连路径均有处理；
- 自动化测试覆盖核心规则，跨端行为有契约测试；
- 没有新增明文秘密、个人数据或无界缓存；
- 相关日志/指标足以定位失败，且不泄露敏感信息；
- 真机功能按测试矩阵验证，或明确标注为待真机验证；
- 文档能让另一位开发者从干净环境复现。

## 7. Git 约定

- 分支建议使用 `codex/<topic>` 或团队约定的短分支名。
- 提交保持单一目的，推荐 Conventional Commits：`feat:`、`fix:`、`docs:`、`test:`、`chore:`。
- 不提交构建产物、IDE 状态、抓包、core dump、覆盖率输出和本地基础设施数据。
- 原始资料目录中的 PDF 与样机属于有意归档资源；不要用通配规则误忽略它们。
