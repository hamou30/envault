# envault

> A CLI tool for managing and encrypting `.env` files across multiple projects with team sharing support.

---

## Installation

```bash
pip install envault
```

Or with [pipx](https://pypa.github.io/pipx/) (recommended):

```bash
pipx install envault
```

---

## Usage

Initialize envault in your project and encrypt your `.env` file:

```bash
# Initialize a new vault in the current project
envault init

# Encrypt your .env file
envault lock --file .env

# Decrypt and load variables into your environment
envault unlock --file .env.vault

# Share encrypted env with your team (exports a shareable bundle)
envault share --output team.env.vault
```

Pull and decrypt a shared vault file from a teammate:

```bash
envault pull team.env.vault --key <your-team-key>
```

---

## Features

- 🔒 AES-256 encryption for `.env` files
- 👥 Team sharing with key-based access control
- 🗂️ Multi-project support from a single CLI
- 🔑 Secure key management via local keystore

---

## License

This project is licensed under the [MIT License](LICENSE).