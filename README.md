# Telegram Invoice Bot

A production-ready Telegram bot built with Python, aiogram v3, and SQLite.

## Features
- **Products Catalog:** Users can browse a list of available products.
- **Order Management:** Users can place orders, view invoices, and simulate payments.
- **Order History:** Users can view their past orders and payment statuses.
- **Admin Controls:** Admins can view all orders across the platform.
- **Clean Architecture:** Modular structure separating bot logic, handlers, services, and database.

## Project Structure
```text
telegram-invoice-bot/
├── main.py                     # Entry point for the bot
├── requirements.txt            # Python dependencies
├── .env.example                # Example environment variables
├── bot/                        # Core bot logic
│   ├── __init__.py
│   └── config.py               # Configuration loading
├── database/                   # Database logic
│   ├── __init__.py
│   └── db.py                   # SQLite database functions using aiosqlite
├── services/                   # Business logic
│   ├── __init__.py
│   └── product_service.py      # Hardcoded products and retrieval logic
└── handlers/                   # Telegram event handlers
    ├── __init__.py
    ├── user_handlers.py        # Handlers for user interactions
    └── admin_handlers.py       # Handlers for admin commands
```

## Setup Instructions

### 1. Prerequisites
- Python 3.9 or higher installed
- A Telegram bot token from [BotFather](https://t.me/BotFather)

### 2. Installation
Clone the repository (or navigate to the folder), then install the required dependencies:

```bash
pip install -r requirements.txt
```

### 3. Configuration
1. Rename `.env.example` to `.env`.
2. Open the `.env` file and replace the placeholder values:
   - `BOT_TOKEN`: Your bot token from BotFather.
   - `ADMIN_ID`: Your personal Telegram User ID (you can get this from bots like `@userinfobot`).

### 4. Running the Bot
Start the bot by running:

```bash
python main.py
```

The bot will automatically create an SQLite database (`database/bot.db`) upon startup.

## Usage
- Start the bot in Telegram by sending `/start`.
- Navigate using the interactive inline buttons to view products, create orders, and simulate payments.
- If you are an admin (your Telegram ID matches `ADMIN_ID` in `.env`), you can send the `/allorders` command to view all orders.
