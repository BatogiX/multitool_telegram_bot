# Multitool Telegram Bot
## Features

- Check file's hash
- Password Manager (Argo2 + AES-GCM) with Zero-Knowledge Proof

## Installation
To install and set up the project, follow these steps:

1. Clone the repository:
    ```sh
    git clone https://github.com/batosgi/multitool_telegram_bot.git
    ```

2. Navigate into the project directory:
    ```sh
    cd multitool_telegram_bot
    ```
   
3. Create a virtual environment:
    ```sh
   python -m venv .venv
   ```
   
4. Activate the virtual environment:
   - For Windows (Git Bash):
        ```sh
        source .venv/Scripts/activate
        ```
   - For macOS/Linux:
        ```sh
        source .venv/bin/activate
        ```

5. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

### Setup environment variables:
- ``BOT_TOKEN=``

Either:

- `KEY_VALUE_DB_URL=`
- `RELATIONAL_DB_URL=`

Or:
- `KEY_VALUE_DB_HOST=`
- `KEY_VALUE_DB_PORT=`
- `KEY_VALUE_DB_USERNAME=`
- `KEY_VALUE_DB_PASSWORD=`

And:
- `RELATIONAL_DB_HOST=`
- `RELATIONAL_DB_PORT=`
- `RELATIONAL_DB_USERNAME=`
- `RELATIONAL_DB_PASSWORD=`
- `RELATIONAL_DB_NAME=`   

## Usage
To start the bot, run the following command:
```sh
python main.py
```
