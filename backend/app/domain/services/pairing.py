"""配对领域服务：生成短期配对码，claim 换取设备绑定（ADR-008 无鉴权，凭据为占位）。"""

import hashlib
import secrets
from datetime import UTC, datetime

from ulid import ULID

from app.core.config import settings
from app.core.errors import AppError, ErrorCode
from app.core.logging import get_logger
from app.repositories.device import DeviceRepository
from app.repositories.pairing import PairingSessionRepository

log = get_logger("app.domain.pairing")


def _hash_code(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


def _gen_code() -> str:
    alphabet = "0123456789"
    return "".join(secrets.choice(alphabet) for _ in range(settings.pairing_code_length))


class PairingService:
    def __init__(
        self,
        session_repo: PairingSessionRepository,
        device_repo: DeviceRepository,
    ) -> None:
        self.session_repo = session_repo
        self.device_repo = device_repo

    async def create_session(self) -> tuple[str, str, datetime]:
        code = _gen_code()
        session_id = f"ps_{ULID()}"
        ps = await self.session_repo.create(session_id, _hash_code(code))
        log.info("pairing_session_created", session_id=session_id)
        return session_id, code, ps.expires_at

    async def claim(
        self,
        code: str,
        device_id: str,
        firmware_version: str | None = None,
    ) -> str:
        ps = await self.session_repo.get_by_code_hash(_hash_code(code))
        if ps is None:
            raise AppError(ErrorCode.NOT_FOUND, "invalid pairing code", 404)
        if ps.claimed_at is not None:
            raise AppError(ErrorCode.CONFLICT, "pairing code already claimed", 409)
        if ps.expires_at < datetime.now(UTC):
            raise AppError(ErrorCode.EXPIRED, "pairing code expired", 410)

        device = await self.device_repo.get(device_id)
        if device is None:
            await self.device_repo.create(device_id, firmware_version=firmware_version)
        else:
            await self.device_repo.touch(device_id, firmware_version=firmware_version)

        await self.session_repo.claim(ps.id, device_id)
        credential = f"devtok_{ULID()}"  # 占位凭据，ADR-008 不强制校验
        log.info("device_claimed", device_id=device_id, session_id=ps.id)
        return credential
