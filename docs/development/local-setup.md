# Local Development Setup

Instructions for setting up the `store` project on a local machine (Phase 1 foundation).

## Prerequisites

- **Python 3.12+** (Python 3.12.3 tested)
- **Git**
- **PostgreSQL** — required for the target architecture. For local development,
  see the PostgreSQL setup section below.

## 1. Python virtual environment

Create and activate a virtual environment in the repository root (`.venv` is
recommended and already Git-ignored):

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows (Powershell): .venv\Scripts\activate
```

Upgrade pip inside the environment:

```bash
python -m pip install --upgrade pip
```

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

This installs Django 5.2 LTS plus the project dependencies (DRF, Pillow,
django-phonenumber-field, psycopg for PostgreSQL, celery, redis, etc.).

Verify:

```bash
python -c "import django; print(django.get_version())"
# -> 5.2.x
```

## 3. Environment variables

Copy the example file and edit it:

```bash
cp .env.example .env
```

`.env` is local-only and Git-ignored. Generate a real secret key in `.env`:

```bash
# Linux/macOS
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Windows (Powershell)
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Relevant variables:

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Django secret key (required, no default). |
| `DEBUG` | `True` for development. |
| `ALLOWED_HOSTS` | Comma-separated host allow-list. |
| `DATABASE_URL` | Preferred DB config (see below). |
| `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | Fallback DB config (used when `DATABASE_URL` is unset). |
| `EMAIL_*` | Email backend/host settings. |

## 4. PostgreSQL local setup

> **Current status (WSL environment):** PostgreSQL is **required** for the target
> architecture, but a PostgreSQL **server is not currently installed** in the
> WSL environment where this project is developed. The Django-side configuration
> for PostgreSQL is already prepared (see below), but a **local PostgreSQL server
> must be installed and running** before the PostgreSQL acceptance criterion for
> this phase is considered complete. Until then the project runs on the SQLite
> fallback for local development only.

The project reads the database config from `DATABASE_URL` (or the `DB_*`
fallbacks). To use PostgreSQL locally:

1. Install PostgreSQL, e.g. on Debian/Ubuntu:

   ```bash
   sudo apt-get install postgresql postgresql-contrib
   ```

   (Adjust for your OS; this step requires administrator privileges.)

2. Create a database and user (adjust names/passwords as you wish, then put
   them in `.env`):

   ```bash
   sudo -u postgres psql
   ```

   ```sql
   CREATE USER store WITH PASSWORD 'change-me';
   CREATE DATABASE store OWNER store;
   ```

3. In `.env`, set:

   ```dotenv
   DATABASE_URL=postgresql://store:change-me@localhost:5432/store
   ```

   (Or set `DB_ENGINE=django.db.backends.postgresql`,
   `DB_NAME=store`, `DB_USER=store`, `DB_PASSWORD=change-me`.)

If `DATABASE_URL` and `DB_ENGINE` are left as their defaults, the project falls
back to a local **SQLite** file (`db.sqlite3`) for zero-configuration
development, which is convenient but intended only as a local convenience.

## 5. Migrations and tests

Run migrations:

```bash
python manage.py makemigrations --check   # confirms no missing migrations
python manage.py migrate --plan           # previews what will be applied
python manage.py migrate                  # applies migrations
```

Run the project checks and tests:

```bash
python manage.py check
python manage.py check --deploy
python manage.py test
```

Run the local development server:

```bash
python manage.py runserver
```

Then open:
- Homepage: <http://127.0.0.1:8000/>
- Admin: <http://127.0.0.1:8000/securelogin/>

## Notes

- PostgreSQL is the target production database; the current defaults favor an
  easy local SQLite start. Migrate the app data in a later phase, not here.
- Never commit `.env`; only `.env.example` (placeholders) is tracked.