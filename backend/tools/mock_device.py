"""模拟设备 CLI：配对 / publish 事件 / 收 ack / 断网重发 / 收命令。

供固件团队无真机时验证后端接口（ADR-008：匿名连接，无需凭据）。

用法（在 backend 目录下）：
  uv run python tools/mock_device.py pair --base-url http://localhost:8000
  uv run python tools/mock_device.py run --device-id dev_01JZ...
  uv run python tools/mock_device.py replay --device-id dev_01JZ...
"""

import argparse
import asyncio
import json
from datetime import UTC, datetime

import aiomqtt
import httpx
from ulid import ULID

TOPIC_PREFIX = "foxsay/v1/devices"


def now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def make_envelope(device_id: str, msg_type: str, payload: dict) -> dict:
    return {
        "schema_version": "1.0",
        "message_id": str(ULID()),
        "device_id": device_id,
        "sent_at": now_iso(),
        "clock_synced": True,
        "type": msg_type,
        "payload": payload,
    }


async def cmd_pair(args: argparse.Namespace) -> None:
    async with httpx.AsyncClient(base_url=args.base_url, timeout=10) as client:
        r = await client.post("/v1/device-pairing/sessions", json={})
        r.raise_for_status()
        sess = r.json()
        code = sess["code"]
        device_id = args.device_id or f"dev_{ULID()}"
        r2 = await client.post(
            "/v1/device-pairing/claim",
            json={"code": code, "device_id": device_id, "firmware_version": "0.1.0"},
        )
        r2.raise_for_status()
        claim = r2.json()
    print(f"device_id={device_id}")
    print(f"credential={claim['credential']}")
    print(f"session_id={sess['session_id']}")
    print("后续用： uv run python tools/mock_device.py run --device-id " + device_id)


async def cmd_run(args: argparse.Namespace) -> None:
    device_id = args.device_id
    presence = make_envelope(
        device_id,
        "device.presence",
        {
            "online": True,
            "firmware_version": "0.1.0",
            "content_version": "2026.07.11.1",
            "network": "wifi",
            "posture": "upright",
            "free_heap_bytes": 131072,
            "reset_reason": "power_on",
        },
    )
    async with aiomqtt.Client(
        hostname=args.broker_host,
        port=args.broker_port,
        identifier=f"mock_{device_id}",
    ) as client:
        await client.publish(
            f"{TOPIC_PREFIX}/{device_id}/presence",
            json.dumps(presence),
            qos=1,
            retain=True,
        )
        print("[presence] published")
        await client.subscribe(f"{TOPIC_PREFIX}/{device_id}/acks")
        await client.subscribe(f"{TOPIC_PREFIX}/{device_id}/commands")

        for i in range(args.events):
            evt = make_envelope(
                device_id,
                "study.card_action",
                {
                    "session_id": str(ULID()),
                    "bundle_version": "2026.07.11.1",
                    "card_id": f"card_{i}",
                    "card_type": "vocabulary",
                    "action": "view_next",
                    "device_sequence": i,
                },
            )
            await client.publish(
                f"{TOPIC_PREFIX}/{device_id}/events", json.dumps(evt), qos=1
            )
            print(f"[event] {i} message_id={evt['message_id']}")

        print("waiting for acks/commands (Ctrl-C to stop)...")
        async for message in client.messages:
            topic = str(message.topic)
            raw = message.payload.decode() if message.payload else "{}"
            print(f"[recv] {topic} {raw}")
            if topic.endswith("/commands"):
                cmd = json.loads(raw)
                ack = make_envelope(
                    device_id,
                    "message.ack",
                    {
                        "correlation_id": cmd["message_id"],
                        "status": "succeeded",
                        "error_code": None,
                        "detail": None,
                    },
                )
                await client.publish(
                    f"{TOPIC_PREFIX}/{device_id}/acks", json.dumps(ack), qos=1
                )
                print(f"[ack] replied to {cmd['message_id']}")


async def cmd_replay(args: argparse.Namespace) -> None:
    """断网重发：同一 message_id 发两次，验证服务端幂等不重复计数。"""
    device_id = args.device_id
    evt = make_envelope(
        device_id,
        "study.card_action",
        {
            "session_id": "ses_replay",
            "bundle_version": "2026.07.11.1",
            "card_id": "card_replay",
            "card_type": "formula",
            "action": "mark_difficult",
            "device_sequence": 1,
        },
    )
    async with aiomqtt.Client(
        hostname=args.broker_host,
        port=args.broker_port,
        identifier=f"mock_replay_{device_id}",
    ) as client:
        for attempt in (1, 2):
            await client.publish(
                f"{TOPIC_PREFIX}/{device_id}/events", json.dumps(evt), qos=1
            )
            print(f"[replay] attempt {attempt} message_id={evt['message_id']}")
            await asyncio.sleep(1)
        await client.subscribe(f"{TOPIC_PREFIX}/{device_id}/acks")
        print("waiting for ack (should receive two acks with same correlation_id)...")
        async for message in client.messages:
            print(f"[recv] {message.topic} {message.payload.decode()}")


def main() -> None:
    p = argparse.ArgumentParser(description="FoxSay mock device")
    sub = p.add_subparsers(dest="cmd", required=True)

    pp = sub.add_parser("pair", help="配对：创建配对码并 claim 设备")
    pp.add_argument("--base-url", default="http://localhost:8000")
    pp.add_argument("--device-id", default=None)
    pp.set_defaults(func=cmd_pair)

    rp = sub.add_parser("run", help="连接并上报事件、收 ack 与命令")
    rp.add_argument("--device-id", required=True)
    rp.add_argument("--broker-host", default="localhost")
    rp.add_argument("--broker-port", type=int, default=1883)
    rp.add_argument("--events", type=int, default=5)
    rp.set_defaults(func=cmd_run)

    rep = sub.add_parser("replay", help="断网重发幂等测试")
    rep.add_argument("--device-id", required=True)
    rep.add_argument("--broker-host", default="localhost")
    rep.add_argument("--broker-port", type=int, default=1883)
    rep.set_defaults(func=cmd_replay)

    args = p.parse_args()
    asyncio.run(args.func(args))


if __name__ == "__main__":
    main()
