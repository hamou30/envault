"""Encryption and decryption utilities for envault using AES-GCM."""

import os
import base64
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


NONCE_SIZE = 12  # bytes, standard for AES-GCM
KEY_SIZE = 32    # bytes, AES-256


def derive_key(passphrase: str, salt: bytes) -> bytes:
    """Derive a 256-bit key from a passphrase using PBKDF2-HMAC-SHA256."""
    return hashlib.pbkdf2_hmac(
        "sha256",
        passphrase.encode("utf-8"),
        salt,
        iterations=200_000,
        dklen=KEY_SIZE,
    )


def encrypt(plaintext: str, passphrase: str) -> str:
    """Encrypt plaintext with a passphrase.

    Returns a base64-encoded string: salt(16) + nonce(12) + ciphertext.
    """
    salt = os.urandom(16)
    nonce = os.urandom(NONCE_SIZE)
    key = derive_key(passphrase, salt)

    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)

    blob = salt + nonce + ciphertext
    return base64.b64encode(blob).decode("utf-8")


def decrypt(encoded: str, passphrase: str) -> str:
    """Decrypt a base64-encoded blob produced by encrypt().

    Raises ValueError on wrong passphrase or corrupted data.
    """
    try:
        blob = base64.b64decode(encoded.encode("utf-8"))
    except Exception as exc:
        raise ValueError("Invalid encrypted data: not valid base64.") from exc

    if len(blob) < 16 + NONCE_SIZE + 16:  # salt + nonce + min GCM tag
        raise ValueError("Invalid encrypted data: payload too short.")

    salt = blob[:16]
    nonce = blob[16:16 + NONCE_SIZE]
    ciphertext = blob[16 + NONCE_SIZE:]

    key = derive_key(passphrase, salt)
    aesgcm = AESGCM(key)

    try:
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    except Exception as exc:
        raise ValueError("Decryption failed: wrong passphrase or corrupted data.") from exc

    return plaintext.decode("utf-8")
