"""单元测试：StudyEventService 幂等入库与难点投影逻辑（用 fake repos，不依赖 DB）。"""

from app.domain.models import Device
from app.domain.schemas import Envelope
from app.domain.services.study_events import StudyEventService


class FakeDeviceRepo:
    def __init__(self) -> None:
        self.devices: dict[str, Device] = {}

    async def get(self, device_id: str) -> Device | None:
        return self.devices.get(device_id)

    async def create(self, device_id, name=None, firmware_version=None) -> Device:
        device = Device(id=device_id, name=name, firmware_version=firmware_version)
        self.devices[device_id] = device
        return device

    async def touch(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        return None


class FakeEventRepo:
    def __init__(self) -> None:
        self.events: set[str] = set()
        self.progress: dict[tuple[str, str], str | None] = {}

    async def insert(self, event) -> bool:
        if event.message_id in self.events:
            return False
        self.events.add(event.message_id)
        return True

    async def upsert_progress(self, device_id, card_id, *, difficulty=None) -> None:
        self.progress[(device_id, card_id)] = difficulty


def make_envelope(message_id: str = "01AAA", action: str = "view_next") -> Envelope:
    return Envelope(
        schema_version="1.0",
        message_id=message_id,
        device_id="dev_1",
        sent_at="2026-07-11T05:00:00Z",
        clock_synced=True,
        type="study.card_action",
        payload={
            "session_id": "ses_1",
            "bundle_version": "2026.07.11.1",
            "card_id": "card_1",
            "card_type": "vocabulary",
            "action": action,
        },
    )


async def test_ingest_new_event_returns_true():
    svc = StudyEventService(FakeDeviceRepo(), FakeEventRepo())
    assert await svc.ingest(make_envelope()) is True


async def test_ingest_duplicate_returns_false():
    repo = FakeEventRepo()
    svc = StudyEventService(FakeDeviceRepo(), repo)
    env = make_envelope("01DUP")
    assert await svc.ingest(env) is True
    assert await svc.ingest(env) is False  # 重投不重复计数


async def test_mark_difficult_sets_difficulty():
    repo = FakeEventRepo()
    svc = StudyEventService(FakeDeviceRepo(), repo)
    await svc.ingest(make_envelope("01DIFF", action="mark_difficult"))
    assert repo.progress[("dev_1", "card_1")] == "difficult"


async def test_view_next_does_not_set_difficulty():
    repo = FakeEventRepo()
    svc = StudyEventService(FakeDeviceRepo(), repo)
    await svc.ingest(make_envelope("01VIEW", action="view_next"))
    assert repo.progress[("dev_1", "card_1")] is None


async def test_ingest_creates_device_if_missing():
    device_repo = FakeDeviceRepo()
    svc = StudyEventService(device_repo, FakeEventRepo())
    await svc.ingest(make_envelope("01NEWDEV"))
    assert "dev_1" in device_repo.devices
