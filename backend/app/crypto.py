import base64
import hashlib
import json

from cryptography.fernet import Fernet

from .config import settings


def _fernet() -> Fernet:
    # Deriva una clave Fernet (32 bytes urlsafe-base64) desde APP_SECRET_KEY.
    key = base64.urlsafe_b64encode(hashlib.sha256(settings.app_secret_key.encode()).digest())
    return Fernet(key)


def encrypt_json(data: dict) -> bytes:
    return _fernet().encrypt(json.dumps(data).encode())


def decrypt_json(blob: bytes) -> dict:
    return json.loads(_fernet().decrypt(bytes(blob)).decode())
