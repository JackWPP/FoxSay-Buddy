"""MQTT 中台桥接。

连 broker，订阅所有设备 topic，把消息分发到 handlers。
本文件为 task4 最小可运行版：连接、订阅、结构化日志。
task7 会扩展 _dispatch 引入 presence/events/acks handlers 与 publisher。
"""

import asyncio
import json

import aiomqtt

from app.core.config import settings
from app.core.logging import get_logger

log = get_logger("app.mqtt.bridge")

DEVICE_TOPIC_PREFIX = "foxsay/v1/devices/"


class MQTTBridge:
    def __init__(self, session_factory=None) -> None:
        self._task: asyncio.Task | None = None
        self._stop = asyncio.Event()
        self.connected = False
        self._client: aiomqtt.Client | None = None
        self._session_factory = session_factory
        self._router = None
        self._publisher = None

    @property
    def publisher(self):
        if self._publisher is None:
            from app.mqtt.publisher import Publisher

            self._publisher = Publisher(self)
        return self._publisher

    async def start(self) -> None:
        if self._session_factory is not None:
            from app.mqtt.router import MQTTRouter

            self._router = MQTTRouter(self._session_factory, self.publisher)
        self._task = asyncio.create_task(self._run(), name="mqtt-bridge")
        log.info(
            "mqtt_bridge_starting",
            host=settings.mqtt_broker_host,
            port=settings.mqtt_broker_port,
        )

    async def stop(self) -> None:
        self._stop.set()
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except (asyncio.CancelledError, Exception):
                pass
        log.info("mqtt_bridge_stopped")

    async def publish(self, topic: str, payload: dict, qos: int | None = None) -> None:
        """发布消息。task7 由 publisher 复用。"""
        if self._client is None:
            log.warning("mqtt_publish_no_client", topic=topic)
            return
        await self._client.publish(topic, json.dumps(payload), qos=qos or settings.mqtt_qos)

    async def _run(self) -> None:
        backoff = 1
        while not self._stop.is_set():
            try:
                async with aiomqtt.Client(
                    identifier=settings.mqtt_client_id,
                    hostname=settings.mqtt_broker_host,
                    port=settings.mqtt_broker_port,
                    # 持久会话:服务端重连后补发离线期间的 events/acks。
                    # 设备侧是否持久会话由设备代码控制(见对接指南 §6)。
                    clean_session=False,
                ) as client:
                    self._client = client
                    self.connected = True
                    backoff = 1
                    log.info("mqtt_connected", host=settings.mqtt_broker_host)
                    for suffix in ("presence", "events", "acks"):
                        await client.subscribe(
                            f"{DEVICE_TOPIC_PREFIX}+/{suffix}", qos=settings.mqtt_qos
                        )
                    async for message in client.messages:
                        await self._dispatch(message)
            except asyncio.CancelledError:
                raise
            except Exception as e:  # noqa: BLE001
                self.connected = False
                self._client = None
                log.warning("mqtt_disconnected", error=str(e), backoff=backoff)
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 30)

    async def _dispatch(self, message) -> None:
        try:
            topic = str(message.topic)
            raw = message.payload
            payload_str = raw.decode("utf-8") if isinstance(raw, (bytes, bytearray)) else str(raw)
            data = json.loads(payload_str) if payload_str else {}
        except Exception as e:  # noqa: BLE001
            log.warning("mqtt_msg_parse_failed", topic=str(message.topic), error=str(e))
            return
        if self._router is not None:
            await self._router.route(topic, data)
        else:
            log.info("mqtt_msg", topic=topic, message_id=data.get("message_id"))
