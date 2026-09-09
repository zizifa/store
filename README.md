# Store

Server-rendered Django e-commerce application.

## Stack

- Python 3.12+
- Django 4.2 (a later Django 5.2 upgrade is planned but not yet performed)
- Server-rendered Django Templates (SSR); JSON/AJAX only where interaction requires it
- SQLite for local development; PostgreSQL is the target production database
- Phone-number based accounts; inventory and order flows are server-authoritative

## Project layout

- `manage.py` — Django CLI entry point
- `shop/` — project settings, URLs, WSGI configuration
- `core/`, `accounts/`, `store/`, `carts/`, `order/` — application packages

## Local setup

1. Create and activate a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate    # Windows: venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:

   ```bash
   cp .env.example .env
   # then edit .env and set a real SECRET_KEY
   ```

4. Run migrations and start the server:

   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

## Configuration

Settings are loaded from environment variables via `python-decouple` (see `.env`).
Keep `.env` local; only `.env.example` with placeholder values is committed.

## Development notes

See `docs/` for architecture, feature contracts, and Cline workflow rules
(`docs/cline/`) used by the project.
