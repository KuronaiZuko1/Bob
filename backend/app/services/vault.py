"""
BOB Document Vault Security Service
Provides AES-128-CBC / HMAC-SHA256 authenticated encryption at rest using Fernet.
All files uploaded to Bob are encrypted prior to being written to disk.
"""
import os
import uuid
import hashlib
import base64
from pathlib import Path
from typing import Tuple
from cryptography.fernet import Fernet
from backend.app.core.config import settings

# Storage Directory
STORAGE_DIR = Path(settings.DOCUMENT_STORAGE_PATH).resolve()
STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def _get_fernet() -> Fernet:
    """Derive Fernet cipher from configured 64-char hex ENCRYPTION_KEY."""
    raw_key = bytes.fromhex(settings.ENCRYPTION_KEY)
    # Ensure 32 bytes for Fernet
    if len(raw_key) != 32:
        raw_key = hashlib.sha256(raw_key).digest()
    fernet_key = base64.urlsafe_b64encode(raw_key)
    return Fernet(fernet_key)


def compute_sha256(data: bytes) -> str:
    """Compute SHA-256 digest of original unencrypted payload."""
    return hashlib.sha256(data).hexdigest()


def encrypt_and_store(file_bytes: bytes, original_filename: str) -> Tuple[str, str, int, str]:
    """
    Encrypt file data with Fernet and store on disk.
    Returns:
        (stored_filename, file_path, original_file_size, sha256_checksum)
    """
    checksum = compute_sha256(file_bytes)
    file_size = len(file_bytes)

    cipher = _get_fernet()
    encrypted_payload = cipher.encrypt(file_bytes)

    # Secure randomized storage filename
    ext = Path(original_filename).suffix.lower()
    stored_filename = f"{uuid.uuid4().hex}{ext}.enc"
    destination = STORAGE_DIR / stored_filename

    with open(destination, "wb") as f:
        f.write(encrypted_payload)

    return stored_filename, str(destination), file_size, checksum


def retrieve_and_decrypt(stored_filename: str) -> bytes:
    """
    Read an encrypted document from disk and return decrypted original bytes.
    """
    file_path = STORAGE_DIR / stored_filename
    if not file_path.exists():
        raise FileNotFoundError(f"Document file {stored_filename} not found in vault")

    with open(file_path, "rb") as f:
        encrypted_payload = f.read()

    cipher = _get_fernet()
    return cipher.decrypt(encrypted_payload)


def delete_stored_file(stored_filename: str) -> bool:
    """
    Securely delete an encrypted document from disk.
    """
    file_path = STORAGE_DIR / stored_filename
    if file_path.exists():
        try:
            # Overwrite with zeros before unlinking for data wiping
            size = file_path.stat().st_size
            with open(file_path, "wb") as f:
                f.write(b"\x00" * size)
            file_path.unlink()
            return True
        except Exception:
            if file_path.exists():
                file_path.unlink()
            return True
    return False
