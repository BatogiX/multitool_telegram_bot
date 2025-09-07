# Multitool Telegram Bot

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://docs.pydantic.dev/latest/contributing/#badges)

## Features

- [Verify File's Checksum](src/helpers/hash_menu_helper/hash_menu_fsm.py)
- [Password Manager (Argon2 + AES-256-GCM) with Zero-Knowledge Proof](src/helpers/pwd_mgr_helper/pwd_mgr_crypto.py)
- [Generate Random Password](src/helpers/gen_rand_pwd_helper/gen_rand_pwd_cb.py)

## Installation

To install and set up the project, follow these steps:

1. Clone
   ```sh
   git clone ...
   ```

2. ```sh
   cd multitool_telegram_bot
   ```

3. Create a virtual environment:
   ```sh
   uv venv
   ```

4. Install the required dependencies:
    ```sh
    uv sync
    ```

5. Install specific dependencies for example:
    ```sh
    uv sync --extra redis --extra postgresql --inexact
    ```

## Usage

### Setup environment variables:

- ``BOT_TOKEN=``
- ``DB_SQL_URL=``
- ``DB_NOSQL_URL=``
- ``CRYPTO_PEPPER=``

### To start the bot, run the following command:
```sh
uv run src/main.py
```
