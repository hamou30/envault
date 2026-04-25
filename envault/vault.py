"""Vault file management — read/write encrypted .env vault files."""

import json
import os
from pathlib import Path
from typing import Optional

from envault.crypto import encrypt, decrypt

DEFAULT_VAULT_FILENAME = ".envault"


class VaultNotFoundError(FileNotFoundError):
    pass


class VaultCorruptedError(ValueError):
    pass


def _vault_path(directory: Optional[str] = None) -> Path:
    base = Path(directory) if directory else Path.cwd()
    return base / DEFAULT_VAULT_FILENAME


def vault_exists(directory: Optional[str] = None) -> bool:
    return _vault_path(directory).exists()


def write_vault(secrets: dict, passphrase: str, directory: Optional[str] = None) -> Path:
    """Serialize secrets dict to JSON, encrypt it, and write to vault file."""
    plaintext = json.dumps(secrets)
    ciphertext = encrypt(plaintext, passphrase)
    path = _vault_path(directory)
    path.write_text(ciphertext)
    return path


def read_vault(passphrase: str, directory: Optional[str] = None) -> dict:
    """Read vault file, decrypt it, and return secrets as a dict."""
    path = _vault_path(directory)
    if not path.exists():
        raise VaultNotFoundError(f"No vault found at {path}")
    ciphertext = path.read_text().strip()
    try:
        plaintext = decrypt(ciphertext, passphrase)
    except Exception as exc:
        raise VaultCorruptedError("Failed to decrypt vault — wrong passphrase or corrupted file.") from exc
    try:
        return json.loads(plaintext)
    except json.JSONDecodeError as exc:
        raise VaultCorruptedError("Vault decrypted but contains invalid JSON.") from exc


def update_vault(key: str, value: str, passphrase: str, directory: Optional[str] = None) -> None:
    """Add or update a single key in the vault."""
    secrets = read_vault(passphrase, directory) if vault_exists(directory) else {}
    secrets[key] = value
    write_vault(secrets, passphrase, directory)


def delete_from_vault(key: str, passphrase: str, directory: Optional[str] = None) -> bool:
    """Remove a key from the vault. Returns True if key existed."""
    secrets = read_vault(passphrase, directory)
    existed = key in secrets
    secrets.pop(key, None)
    write_vault(secrets, passphrase, directory)
    return existed
