# BudgetDiary

Discord bot for daily income/outcome tracking with PIN-protected actions, JSON storage, and Excel exports. The codebase is now modular (cogs + services) and supports multiple users per guild with per-user regions and currencies.

## Features
- Slash commands with embeds, dropdowns, modals, and confirm buttons.
- PIN verification in DM for every balance-changing command.
- JSON storage shaped like a Mongo collection (`data/store/*.json`), one user per document key.
- CRUD for income/outcome categories (with emoji support).
- Record income, outcome (select income source), and transfers between income types.
- Daily, monthly, yearly reports, top outcome finder, per-income balances, monthly curation, and Excel export.
- Region-aware currency formatting (USA = USD, JAPAN = JPY, INDONESIA = IDR).

## Commands (high level)
- `\register` — set PIN, language, region, email.
- `\profile`, `\set_language`, `\set_region`.
- `\add_category`, `\edit_category`, `\delete_category`, `\list_categories`.
- `\add_income`, `\add_outcome`, `\transfer_income` (all PIN-gated).
- Reports: `\daily_income`, `\daily_outcome`, `\monthly_income`, `\monthly_outcome`, `\yearly_outcome`, `\top_outcome`, `\balance`, `\monthly_curation`.
- Export: `\export_month` -> Excel download.

## Requirements
- Python 3.9+
- nextcord
- emoji
- openpyxl

Install with:

```bash
pip install -r requirements.txt
```

## ENV
Create `_env.py` alongside `main.py`:

```python
class ENV:
    TOKEN = "<discord bot token>"
```

## Running

```bash
python main.py
```

Slash commands will sync automatically; by default they are global. Joined guild IDs are persisted to `list_guild.json`.
