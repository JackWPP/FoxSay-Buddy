from enum import StrEnum


class ErrorCode(StrEnum):
    """稳定机器码，与 MQTT ack error_code 对齐（见 04 §7）。"""

    EXPIRED = "expired"
    UNSUPPORTED_SCHEMA = "unsupported_schema"
    UNSUPPORTED_COMMAND = "unsupported_command"
    INVALID_PAYLOAD = "invalid_payload"
    BUSY = "busy"
    DOWNLOAD_FAILED = "download_failed"
    CHECKSUM_MISMATCH = "checksum_mismatch"
    INSUFFICIENT_STORAGE = "insufficient_storage"
    INTERNAL_ERROR = "internal_error"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"


class AppError(Exception):
    def __init__(self, code: ErrorCode, detail: str, status_code: int = 400) -> None:
        self.code = code
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)
