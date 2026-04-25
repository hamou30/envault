"""Tests for vault read/write operations."""

import json
import pytest
from pathlib import Path

from envault.vault import (
    write_vault,
    read_vault,
    update_vault,
    delete_from_vault,
    vault_exists,
    VaultNotFoundError,
    VaultCorruptedError,
)

PASSPHRASE = "super-secret-passphrase"
SECRETS = {"DB_URL": "postgres://localhost/mydb", "API_KEY": "abc123"}


def test_write_and_read_vault(tmp_path):
    write_vault(SECRETS, PASSPHRASE, directory=str(tmp_path))
    result = read_vault(PASSPHRASE, directory=str(tmp_path))
    assert result == SECRETS


def test_vault_exists_after_write(tmp_path):
    assert not vault_exists(directory=str(tmp_path))
    write_vault(SECRETS, PASSPHRASE, directory=str(tmp_path))
    assert vault_exists(directory=str(tmp_path))


def test_read_vault_not_found_raises(tmp_path):
    with pytest.raises(VaultNotFoundError):
        read_vault(PASSPHRASE, directory=str(tmp_path))


def test_read_vault_wrong_passphrase_raises(tmp_path):
    write_vault(SECRETS, PASSPHRASE, directory=str(tmp_path))
    with pytest.raises(VaultCorruptedError):
        read_vault("wrong-passphrase", directory=str(tmp_path))


def test_update_vault_adds_key(tmp_path):
    write_vault(SECRETS, PASSPHRASE, directory=str(tmp_path))
    update_vault("NEW_KEY", "new_value", PASSPHRASE, directory=str(tmp_path))
    result = read_vault(PASSPHRASE, directory=str(tmp_path))
    assert result["NEW_KEY"] == "new_value"
    assert result["DB_URL"] == SECRETS["DB_URL"]


def test_update_vault_overwrites_key(tmp_path):
    write_vault(SECRETS, PASSPHRASE, directory=str(tmp_path))
    update_vault("API_KEY", "newkey999", PASSPHRASE, directory=str(tmp_path))
    result = read_vault(PASSPHRASE, directory=str(tmp_path))
    assert result["API_KEY"] == "newkey999"


def test_update_vault_creates_if_missing(tmp_path):
    update_vault("ONLY_KEY", "only_val", PASSPHRASE, directory=str(tmp_path))
    result = read_vault(PASSPHRASE, directory=str(tmp_path))
    assert result == {"ONLY_KEY": "only_val"}


def test_delete_from_vault_existing_key(tmp_path):
    write_vault(SECRETS, PASSPHRASE, directory=str(tmp_path))
    existed = delete_from_vault("API_KEY", PASSPHRASE, directory=str(tmp_path))
    assert existed is True
    result = read_vault(PASSPHRASE, directory=str(tmp_path))
    assert "API_KEY" not in result


def test_delete_from_vault_missing_key(tmp_path):
    write_vault(SECRETS, PASSPHRASE, directory=str(tmp_path))
    existed = delete_from_vault("NONEXISTENT", PASSPHRASE, directory=str(tmp_path))
    assert existed is False
