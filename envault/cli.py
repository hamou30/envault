"""CLI entry point for envault.

Provides commands for initializing vaults, importing/exporting .env files,
and managing secrets across projects.
"""

import sys
import os
import click
from pathlib import Path

from .vault import (
    vault_exists,
    write_vault,
    read_vault,
    update_vault,
    delete_key,
    _vault_path,
)
from .dotenv_io import parse_dotenv, write_dotenv, merge_dotenv
from .exceptions import (
    VaultNotFoundError,
    VaultCorruptedError,
    PassphraseError,
    DotEnvParseError,
)


def _prompt_passphrase(confirm: bool = False) -> str:
    """Prompt the user for a passphrase, optionally asking to confirm it."""
    passphrase = click.prompt("Passphrase", hide_input=True)
    if confirm:
        confirmed = click.prompt("Confirm passphrase", hide_input=True)
        if passphrase != confirmed:
            click.echo("Error: passphrases do not match.", err=True)
            sys.exit(1)
    return passphrase


@click.group()
@click.version_option(package_name="envault")
def cli():
    """envault — encrypt and manage your .env files."""
    pass


@cli.command("init")
@click.option("--dir", "project_dir", default=".", help="Project directory (default: current).")
def init_cmd(project_dir):
    """Initialize a new vault in the project directory."""
    project_dir = Path(project_dir).resolve()
    if vault_exists(project_dir):
        click.echo("A vault already exists in this directory.")
        sys.exit(1)

    passphrase = _prompt_passphrase(confirm=True)
    write_vault({}, passphrase, project_dir)
    click.echo(f"Vault initialized at {_vault_path(project_dir)}")


@cli.command("import")
@click.argument("env_file", default=".env")
@click.option("--dir", "project_dir", default=".", help="Project directory.")
def import_cmd(env_file, project_dir):
    """Import a .env file into the vault."""
    project_dir = Path(project_dir).resolve()
    env_path = Path(env_file)

    if not env_path.exists():
        click.echo(f"Error: file '{env_file}' not found.", err=True)
        sys.exit(1)

    try:
        new_vars = parse_dotenv(env_path)
    except DotEnvParseError as e:
        click.echo(f"Parse error: {e}", err=True)
        sys.exit(1)

    passphrase = _prompt_passphrase()

    try:
        if vault_exists(project_dir):
            existing = read_vault(passphrase, project_dir)
            merged = merge_dotenv(existing, new_vars)
            write_vault(merged, passphrase, project_dir)
        else:
            write_vault(new_vars, passphrase, project_dir)
    except (VaultNotFoundError, VaultCorruptedError, PassphraseError) as e:
        click.echo(f"Vault error: {e}", err=True)
        sys.exit(1)

    click.echo(f"Imported {len(new_vars)} variable(s) from '{env_file}'.")


@cli.command("export")
@click.argument("env_file", default=".env")
@click.option("--dir", "project_dir", default=".", help="Project directory.")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing file.")
def export_cmd(env_file, project_dir, overwrite):
    """Export vault contents to a .env file."""
    project_dir = Path(project_dir).resolve()
    env_path = Path(env_file)

    if env_path.exists() and not overwrite:
        click.echo(f"'{env_file}' already exists. Use --overwrite to replace it.", err=True)
        sys.exit(1)

    passphrase = _prompt_passphrase()

    try:
        secrets = read_vault(passphrase, project_dir)
    except VaultNotFoundError:
        click.echo("No vault found. Run 'envault init' first.", err=True)
        sys.exit(1)
    except (VaultCorruptedError, PassphraseError) as e:
        click.echo(f"Vault error: {e}", err=True)
        sys.exit(1)

    write_dotenv(secrets, env_path)
    click.echo(f"Exported {len(secrets)} variable(s) to '{env_file}'.")


@cli.command("set")
@click.argument("key")
@click.argument("value")
@click.option("--dir", "project_dir", default=".", help="Project directory.")
def set_cmd(key, value, project_dir):
    """Set a single key/value in the vault."""
    project_dir = Path(project_dir).resolve()
    passphrase = _prompt_passphrase()

    try:
        update_vault({key: value}, passphrase, project_dir)
    except VaultNotFoundError:
        click.echo("No vault found. Run 'envault init' first.", err=True)
        sys.exit(1)
    except (VaultCorruptedError, PassphraseError) as e:
        click.echo(f"Vault error: {e}", err=True)
        sys.exit(1)

    click.echo(f"Set '{key}' in vault.")


@cli.command("delete")
@click.argument("key")
@click.option("--dir", "project_dir", default=".", help="Project directory.")
def delete_cmd(key, project_dir):
    """Delete a key from the vault."""
    project_dir = Path(project_dir).resolve()
    passphrase = _prompt_passphrase()

    try:
        delete_key(key, passphrase, project_dir)
    except VaultNotFoundError:
        click.echo("No vault found.", err=True)
        sys.exit(1)
    except (VaultCorruptedError, PassphraseError) as e:
        click.echo(f"Vault error: {e}", err=True)
        sys.exit(1)
    except KeyError:
        click.echo(f"Key '{key}' not found in vault.", err=True)
        sys.exit(1)

    click.echo(f"Deleted '{key}' from vault.")


@cli.command("list")
@click.option("--dir", "project_dir", default=".", help="Project directory.")
@click.option("--show-values", is_flag=True, default=False, help="Print values alongside keys.")
def list_cmd(project_dir, show_values):
    """List all keys stored in the vault."""
    project_dir = Path(project_dir).resolve()
    passphrase = _prompt_passphrase()

    try:
        secrets = read_vault(passphrase, project_dir)
    except VaultNotFoundError:
        click.echo("No vault found.", err=True)
        sys.exit(1)
    except (VaultCorruptedError, PassphraseError) as e:
        click.echo(f"Vault error: {e}", err=True)
        sys.exit(1)

    if not secrets:
        click.echo("Vault is empty.")
        return

    for k, v in sorted(secrets.items()):
        if show_values:
            click.echo(f"{k}={v}")
        else:
            click.echo(k)


if __name__ == "__main__":
    cli()
