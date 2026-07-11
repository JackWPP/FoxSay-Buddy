"""契约测试：验证 schemas/ 下 JSON Schema 与 fixtures 一致。

正例必须通过对应 schema；反例必须被拒绝。schemas 是跨端唯一机器可读契约，
固件与后端共同引用，本测试守护契约不漂移。
"""

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parents[3]
SCHEMAS_DIR = REPO_ROOT / "schemas"
FIXTURES_DIR = SCHEMAS_DIR / "fixtures"

SCHEMAS = {
    "envelope": "envelope.json",
    "presence": "presence.json",
    "study_event": "study_event.json",
    "command": "command.json",
    "ack": "ack.json",
}

VALID_FIXTURES = {
    "envelope": "envelope_valid.json",
    "presence": "presence_valid.json",
    "study_event": "study_event_valid.json",
    "command": "command_content_sync.json",
    "ack": "ack_succeeded.json",
}

INVALID_FIXTURES = {
    "envelope": "envelope_invalid.json",
    "presence": "presence_invalid.json",
    "study_event": "study_event_invalid_action.json",
}


def load_schema(name: str) -> dict:
    return json.loads((SCHEMAS_DIR / SCHEMAS[name]).read_text(encoding="utf-8"))


def load_fixture(filename: str) -> dict:
    return json.loads((FIXTURES_DIR / filename).read_text(encoding="utf-8"))


@pytest.mark.parametrize("key", list(SCHEMAS))
def test_schema_files_exist(key: str) -> None:
    assert (SCHEMAS_DIR / SCHEMAS[key]).exists()


@pytest.mark.parametrize("key", list(VALID_FIXTURES))
def test_valid_fixtures_pass(key: str) -> None:
    schema = load_schema(key)
    fixture = load_fixture(VALID_FIXTURES[key])
    Draft202012Validator(schema).validate(fixture)


@pytest.mark.parametrize("key", list(INVALID_FIXTURES))
def test_invalid_fixtures_rejected(key: str) -> None:
    schema = load_schema(key)
    fixture = load_fixture(INVALID_FIXTURES[key])
    with pytest.raises(Exception):  # noqa: B017, PT011
        Draft202012Validator(schema).validate(fixture)


def test_command_sha256_pattern() -> None:
    """command content.sync 的 sha256 必须是 64 位小写十六进制。"""
    schema = load_schema("command")
    fixture = load_fixture("command_content_sync.json")
    fixture["payload"]["sha256"] = "XYZ"  # 非法
    with pytest.raises(Exception):  # noqa: B017, PT011
        Draft202012Validator(schema).validate(fixture)
