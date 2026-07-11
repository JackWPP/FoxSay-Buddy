# 05 — 开发与交付计划

**状态：Accepted**

计划采用风险优先的 vertical slice：先让“真机点击一张卡 → 断网缓存 → MQTT 上报 → 后端幂等落库 → ack 清除 outbox”完整跑通，再扩页面。

## Phase 0 — 硬件与工具链探针

目标：关闭会改变架构的硬件未知项。

- 建立 ESP-IDF 最小工程并锁定可复现版本；
- 验证 LCD、触控、旋转/坐标、背光、QMI8658、SD、ES7210/ES8311；
- 输出 Flash 分区、内部 heap、PSRAM、draw buffer 和 FPS 基线；
- 验证 Wi-Fi、TLS 时间同步与 MQTT 客户端；
- 记录板卡版本、BSP 来源和 pin mapping。

退出标准：真机显示触摸坐标测试页，能联网发布消息；`TBD-001/002` 关闭；形成 `firmware/README.md` 的一键构建/烧录命令。

## Phase 1 — 工程骨架与契约

目标：从干净环境启动完整本地链路。

- 创建预期单仓库目录；
- 添加 Compose：PostgreSQL、Mosquitto、对象存储与 backend；
- 创建 JSON Schema、示例 fixture 和契约测试；
- 后端 migration、设备模型、MQTT worker、health endpoints；
- 固件配置存储、MQTT lifecycle、结构化诊断；
- 配对策略确认并实现最小闭环。

退出标准：模拟设备与真机都能鉴权连接，只能访问自身 topic；CI 能验证 schema、后端测试和固件编译。

## Phase 2 — P0 竖切闭环

目标：完成第一条可真实使用的数据链路。

- 固件主屏与单词卡最小 UI；
- 本地 card session 与持久化 outbox；
- 后端学习事件幂等入库与业务 ack；
- 断网/重启/重连恢复；
- UI、协议、数据库的端到端测试脚本。

退出标准：在真机断网浏览 100 张卡并重启，联网后事件完整同步、无重复计数、outbox 清空。

## Phase 3 — MVP 功能完整

目标：完成产品 Spec 的全部 P0。

- 公式卡翻面、难点和跳过；
- 姿态休眠、唤醒与快捷音量面板；
- 内容包生成、下载、哈希校验和原子切换；
- OTA、回滚与小批量发布；
- 设备管理、学习查询和必要的运维接口；
- 中文字体/狐狸资源的最终预算与降级路径。

退出标准：所有 P0 验收用例通过；无未解释的 reset；资源预算满足；staging 完成至少一次 OTA 回滚演练。

## Phase 4 — 稳定性与内测

目标：10 台设备、7 天 dogfood。

- 8–24 小时 soak、重连风暴、broker/DB 重启和存储故障演练；
- 配对、同步延迟、reset reason、OTA 指标面板；
- 安全检查、凭据轮换、日志脱敏和备份恢复；
- 建立版本兼容矩阵与 staged rollout；
- 收集误触、字体可读性和实际学习完成率。

退出标准：阻断级缺陷清零；已知限制入文档；形成下一迭代 P1 的真实优先级。

## 测试矩阵

| 层级 | 自动化 | 真机/环境 |
| --- | --- | --- |
| schema | 正反例 JSON、兼容性 fixture | MQTT 抓取消息回放 |
| firmware unit | parser、状态机、outbox、manifest 校验 | 目标板编译与硬件 smoke |
| backend unit | domain service、鉴权、幂等、错误映射 | PostgreSQL/Mosquitto 集成 |
| end-to-end | 模拟设备 publish/ack/content | 真机断网、断电、SD、OTA |
| performance | payload/查询基准 | FPS、heap、启动、8h soak |
| security | schema fuzz、ACL 测试、secret scan | 配对限流、证书轮换、TLS |

## 主要风险与缓解

| 风险 | 影响 | 缓解 |
| --- | --- | --- |
| 原始 UI 样机远大于 320×240，字体/细节无法还原 | 可读性和性能失败 | 真机先做灰盒线框；逐项重绘资源，不直接缩放样机 |
| 中文字库和动画挤占 Flash/RAM | OTA 或运行内存不足 | 字符子集 + SD bundle + LRU；Phase 0 建预算 |
| MQTT QoS 1 重复消息 | 学习统计重复 | message_id 唯一键、业务 ack、幂等 projection |
| 断电破坏内容/outbox | 数据丢失或无法启动 | append/CRC、临时文件、哈希和原子 pointer |
| 全局与页面手势冲突 | 高频误触 | 明确事件优先级、起始区域、真机阈值配置 |
| 实时语音过早扩大范围 | 延期、隐私与网络风险 | MVP 排除；P1 先 HTTPS，再评估 WebRTC |
| 示例分区表未经验证 | OTA image 越界或空间不足 | 依据真实 map 生成并做 bootloader/OTA 测试 |

## 首批建议任务

1. `chore(firmware): add ESP-IDF board probe with pinned toolchain`；
2. `test(firmware): add touch coordinate and rotation diagnostic screen`；
3. `chore(infra): add pinned local compose stack and Mosquitto ACL`；
4. `feat(schemas): define envelope, study event, command and ack schemas`；
5. `feat(backend): ingest study events idempotently and publish business ack`；
6. `feat(firmware): persist bounded outbox and reconcile acknowledgements`；
7. `feat(firmware): implement vocabulary vertical slice on real device`。
