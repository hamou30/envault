"""Shared exception hierarchy for envault."""


class EnvaultError(Exception):
    """Base class for all envault errors."""


class VaultNotFoundError(EnvaultError, FileNotFoundError):
    """Raised when a vault file cannot be located."""


class VaultCorruptedError(EnvaultError, ValueError):
    """Raised when a vault file cannot be decrypted or parsed."""


class DotEnvParseError(EnvaultError, ValueError):
    """Raised when a .env file cannot be parsed."""


class PassphraseError(EnvaultError):
    """Raised when a passphrase is invalid or missing."""

    def __init__(self, message: str = "Invalid or missing passphrase."):
        super().__init__(message)


class KeyNotFoundError(EnvaultError, KeyError):
    """Raised when a requested secret key does not exist in the vault."""

    def __init__(self, key: str):
        self.key = key
        super().__init__(f"Key '{key}' not found in vault.")
