# Local Development Setup

Instructions for setting up the `store` project on a local machine (Phase 1 foundation).

## Prerequisites

- **Python 3.12+** (Python 3.12.3 tested)
- **Git**
- **Docker Desktop / Docker Engine** — used only for the local PostgreSQL
  container (PostgreSQL is the target database; see section 4).

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

## 4. Local PostgreSQL (Docker)

> **Status in this environment:** Docker is **not available** in the WSL distro
> used for development (`docker` and `docker compose` are not on the `PATH`, and
> Docker Desktop's WSL integration is not enabled for this distro). Local
> PostgreSQL therefore could **not** be started here yet. The workflow below is
> the supported local setup and works as soon as Docker is available. Do **not**
> install Docker or system PostgreSQL with `sudo` in this environment.

PostgreSQL is the **target database**. SQLite support in `shop/settings.py` is
kept only temporarily as a fallback for legacy/local recovery while PostgreSQL
is being adopted.

### 4.1 Prerequisites

- Docker Desktop (Windows/macOS) or Docker Engine with the Compose plugin.
  - On Windows, enable **WSL integration** for this distro in Docker Desktop
    settings so `docker` and `docker compose` work from WSL.
- No `sudo` and no system-wide PostgreSQL install are required: Docker is used
  only for the local PostgreSQL container in this phase.

### 4.2 Environment variables

`.env` (local only, Git-ignored) supplies the credentials for both Docker and
Django. Only placeholders live in `.env.example`.

| Variable | Purpose |
|---|---|
| `POSTGRES_DB` | Database name created by the container. |
| `POSTGRES_USER` | Database user created by the container. |
| `POSTGRES_PASSWORD` | Database password (**required** by the compose file). |
| `POSTGRES_PORT` | Local port published on `127.0.0.1` (default `5432`). |
| `DATABASE_URL` | How Django connects, e.g. `postgresql://store:<password>@127.0.0.1:5432/store`. |

Keep `DATABASE_URL` in sync with the `POSTGRES_*` values: the password inside
`DATABASE_URL` must match `POSTGRES_PASSWORD`. No credential is hardcoded in
`infra/docker-compose.yml`, `shop/settings.py`, or documentation.

### 4.3 Start / stop / status

From the repository root:

```bash
# start
docker compose --env-file .env -f infra/docker-compose.yml up -d

# status (container state + health)
docker compose --env-file .env -f infra/docker-compose.yml ps

# stop (keeps the data volume)
docker compose --env-file .env -f infra/docker-compose.yml down

# logs (troubleshooting)
docker compose --env-file .env -f infra/docker-compose.yml logs -f db
```

The container:

- binds PostgreSQL to `127.0.0.1:<POSTGRES_PORT>` only (never `0.0.0.0`);
- stores data in the persistent named volume `store_postgres_data`, so data
  survives `down`/`up` cycles;
- restarts automatically on failure (`restart: unless-stopped`).

### 4.4 Run migrations against PostgreSQL

With PostgreSQL running and `DATABASE_URL` set to the PostgreSQL URL:

```bash
python manage.py migrate --plan            # preview what will be applied
python manage.py migrate                   # create the PostgreSQL schema
python manage.py makemigrations --check    # must report "No changes detected"
```

Do **not** use `--fake` or `--fake-initial` unless there is a diagnosed reason
reported explicitly.

### 4.5 Run Django

```bash
python manage.py runserver
```

Then open:
- Homepage: <http://127.0.0.1:8000/>
- Admin: <http://127.0.0.1:8000/securelogin/>

### 4.6 Troubleshooting basics

| Symptom | Check |
|---|---|
| `docker: command not found` | Docker Desktop is not running, or WSL integration is off for this distro. |
| `connection refused` from Django | Container not running (`... ps`), or `DATABASE_URL` host/port mismatch. |
| Compose errors about `POSTGRES_PASSWORD` | The variable is missing from `.env`; the compose file refuses to start without it. |
| Port already in use | Another service holds `POSTGRES_PORT`; choose another port in `.env`. |
| Data seems "gone" | The volume was removed; verify with `docker volume ls` that `store_postgres_data` exists. |

### 4.7 Legacy SQLite database

`db.sqlite3` at the repository root is the **legacy development database**. It is
Git-ignored and is **not** migrated or copied into PostgreSQL in this phase.
SQLite stays available temporarily via `DATABASE_URL`/`DB_*` fallback, while
PostgreSQL remains the primary target database.

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

- PostgreSQL is the **target database**; the SQLite fallback in settings is
  temporary and intended only for legacy/local recovery. Do not migrate legacy
  SQLite data into PostgreSQL in this phase.
- The PostgreSQL data volume (`store_postgres_data`) is persistent: data
  survives container `down`/`up` cycles.
- Credentials live only in the local `.env` (Git-ignored); `.env.example` carries
  placeholders only. Docker is used for local PostgreSQL only in this phase.
- Never commit `.env` or `db.sqlite3`.