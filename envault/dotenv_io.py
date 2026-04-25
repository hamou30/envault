"""Utilities to parse .env files and export secrets back to them."""

import re
from pathlib import Path
from typing import Optional

_LINE_RE = re.compile(r"^\s*(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.*)$")
_COMMENT_RE = re.compile(r"^\s*#")


def parse_dotenv(path: str) -> dict:
    """Parse a .env file and return a dict of key-value pairs.

    - Ignores blank lines and comments.
    - Strips optional surrounding quotes from values.
    """
    secrets = {}
    for line in Path(path).read_text().splitlines():
        if not line.strip() or _COMMENT_RE.match(line):
            continue
        m = _LINE_RE.match(line)
        if m:
            key = m.group("key")
            value = _strip_quotes(m.group("value").strip())
            secrets[key] = value
    return secrets


def _strip_quotes(value: str) -> str:
    """Remove surrounding single or double quotes if present."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return value[1:-1]
    return value


def write_dotenv(secrets: dict, path: str, overwrite: bool = False) -> None:
    """Write a secrets dict to a .env file.

    If the file already exists and overwrite is False, raises FileExistsError.
    """
    dest = Path(path)
    if dest.exists() and not overwrite:
        raise FileExistsError(f"{path} already exists. Pass overwrite=True to replace it.")
    lines = [f"{key}={value}\n" for key, value in sorted(secrets.items())]
    dest.write_text("".join(lines))


def merge_dotenv(existing_path: str, new_secrets: dict, overwrite_keys: bool = True) -> dict:
    """Merge new_secrets into an existing .env file's contents.

    Returns the merged dict (does not write to disk).
    """
    existing = parse_dotenv(existing_path) if Path(existing_path).exists() else {}
    if overwrite_keys:
        existing.update(new_secrets)
    else:
        for key, value in new_secrets.items():
            existing.setdefault(key, value)
    return existing
