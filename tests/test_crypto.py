"""Tests for envault.crypto encryption/decryption utilities."""

import pytest
from envault.crypto import encrypt, decrypt, derive_key


PASSPHRASE = "super-secret-passphrase"
PLAINTEXT = "DB_PASSWORD=hunter2\nAPI_KEY=abc123\n"


def test_encrypt_returns_string():
    result = encrypt(PLAINTEXT, PASSPHRASE)
    assert isinstance(result, str)
    assert len(result) > 0


def test_encrypt_produces_different_ciphertext_each_time():
    """Random salt/nonce means two encryptions of the same data differ."""
    result1 = encrypt(PLAINTEXT, PASSPHRASE)
    result2 = encrypt(PLAINTEXT, PASSPHRASE)
    assert result1 != result2


def test_decrypt_roundtrip():
    encoded = encrypt(PLAINTEXT, PASSPHRASE)
    decoded = decrypt(encoded, PASSPHRASE)
    assert decoded == PLAINTEXT


def test_decrypt_wrong_passphrase_raises():
    encoded = encrypt(PLAINTEXT, PASSPHRASE)
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt(encoded, "wrong-passphrase")


def test_decrypt_corrupted_data_raises():
    encoded = encrypt(PLAINTEXT, PASSPHRASE)
    # Flip a character in the middle of the payload
    corrupted = encoded[:-10] + "AAAAAAAAAA"
    with pytest.raises(ValueError):
        decrypt(corrupted, PASSPHRASE)


def test_decrypt_invalid_base64_raises():
    with pytest.raises(ValueError, match="not valid base64"):
        decrypt("!!!not-base64!!!", PASSPHRASE)


def test_decrypt_too_short_raises():
    import base64
    short_blob = base64.b64encode(b"tooshort").decode()
    with pytest.raises(ValueError, match="too short"):
        decrypt(short_blob, PASSPHRASE)


def test_derive_key_length():
    key = derive_key("passphrase", b"saltsaltsaltsalt")
    assert len(key) == 32


def test_derive_key_deterministic():
    salt = b"fixed-salt-bytes"
    key1 = derive_key("mypassword", salt)
    key2 = derive_key("mypassword", salt)
    assert key1 == key2


def test_derive_key_different_salts_differ():
    key1 = derive_key("mypassword", b"salt-one-here-xx")
    key2 = derive_key("mypassword", b"salt-two-here-xx")
    assert key1 != key2
