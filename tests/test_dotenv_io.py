"""Tests for .env file parsing and writing utilities."""

import pytest
from pathlib import Path

from envault.dotenv_io import parse_dotenv, write_dotenv, merge_dotenv


SAMPLE_ENV = """# Database config
DB_URL=postgres://localhost/mydb
API_KEY="abc123"
SECRET='my secret'
EMPTY_VAL=

DEBUG=true
"""


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text(SAMPLE_ENV)
    return str(f)


def test_parse_basic_keys(env_file):
    result = parse_dotenv(env_file)
    assert result["DB_URL"] == "postgres://localhost/mydb"
    assert result["DEBUG"] == "true"


def test_parse_strips_double_quotes(env_file):
    result = parse_dotenv(env_file)
    assert result["API_KEY"] == "abc123"


def test_parse_strips_single_quotes(env_file):
    result = parse_dotenv(env_file)
    assert result["SECRET"] == "my secret"


def test_parse_empty_value(env_file):
    result = parse_dotenv(env_file)
    assert result["EMPTY_VAL"] == ""


def test_parse_ignores_comments(env_file):
    result = parse_dotenv(env_file)
    assert "# Database config" not in result
    assert len([k for k in result if k.startswith("#")]) == 0


def test_write_dotenv(tmp_path):
    dest = str(tmp_path / ".env")
    secrets = {"FOO": "bar", "BAZ": "qux"}
    write_dotenv(secrets, dest)
    content = Path(dest).read_text()
    assert "BAZ=qux" in content
    assert "FOO=bar" in content


def test_write_dotenv_raises_if_exists(tmp_path):
    dest = str(tmp_path / ".env")
    Path(dest).write_text("EXISTING=1\n")
    with pytest.raises(FileExistsError):
        write_dotenv({"KEY": "val"}, dest, overwrite=False)


def test_write_dotenv_overwrite(tmp_path):
    dest = str(tmp_path / ".env")
    Path(dest).write_text("OLD=1\n")
    write_dotenv({"NEW": "2"}, dest, overwrite=True)
    assert "NEW=2" in Path(dest).read_text()


def test_merge_dotenv_overwrites_by_default(tmp_path):
    f = tmp_path / ".env"
    f.write_text("KEY=old\n")
    merged = merge_dotenv(str(f), {"KEY": "new", "EXTRA": "yes"})
    assert merged["KEY"] == "new"
    assert merged["EXTRA"] == "yes"


def test_merge_dotenv_no_overwrite(tmp_path):
    f = tmp_path / ".env"
    f.write_text("KEY=original\n")
    merged = merge_dotenv(str(f), {"KEY": "ignored"}, overwrite_keys=False)
    assert merged["KEY"] == "original"
