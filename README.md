# BudgetDiary

A lightweight Discord bot for tracking incomes and expenses without a full database server. All data is stored in JSON so you can host the bot anywhere (Replit, containers, or a tiny VM) and still keep your ledger safe.

## Features

- `/register` — create a profile secured by your PIN.
- `/profile` — view your language, email, and running balance.
- `/categories` — list income or outcome categories scoped to your Discord account.
- `/add_category` — create new categories that fit the way you spend.
- `/transaction` — record incomes or outcomes against categories.
- `/recent` — review the latest transactions.
- `/help` — quick command reference.

## Project layout

```
budget_diary/
├── bot.py                  # Bot bootstrap + extension loader
├── config.py               # Environment-driven paths and defaults
├── models.py               # Dataclasses for users, categories, transactions
├── cogs/                   # Slash commands grouped by responsibility
├── services/               # Business logic and JSON persistence helpers
└── storage/json_store.py   # Tiny JSON wrapper with defaults
```

Data is kept under `data/`:

- `users.json` — registered Discord users.
- `categories.json` — per-user income/outcome categories.
- `transactions.json` — ledger entries keyed by user.
- `templates/categories.json` — default categories automatically applied to new users.

## Setup

1. Install dependencies (Python 3.10+ recommended):

   ```bash
   pip install -r requirements.txt
   ```

2. Provide a Discord bot token via environment variable:

   ```bash
   export DISCORD_BOT_TOKEN="your token here"
   ```

   Optional overrides:

   - `DEFAULT_LANGUAGE` — default language saved for new users (defaults to `en`).
   - `DATA_DIR` — custom directory for JSON storage (defaults to the bundled `data/`).

3. Start the bot:

   ```bash
   python -m budget_diary.bot
   ```

Invite the bot to your server and use `/help` to see the available commands.

## Design notes

- JSON storage is handled by `JsonStore`, which guarantees files and parent folders exist before any reads/writes.
- Services (`user_service.py`, `category_service.py`, `transaction_service.py`) keep business logic DRY and testable, separating it from Discord-specific code.
- Cogs only orchestrate user interaction; they call services to read/write JSON data.
- Default categories live in `data/templates/categories.json`, making it easy to ship opinionated starting points while still allowing per-user customization.
