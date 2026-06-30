# Flask Tasks CRUD API

[![CI](https://github.com/moisesneivert/Flask-Tasks-Crud-Api/actions/workflows/ci.yml/badge.svg)](https://github.com/moisesneivert/Flask-Tasks-Crud-Api/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-black)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Production-style REST API for task management built with Flask and SQLAlchemy. The project implements complete CRUD operations, validation, filtering, pagination, database migrations, automated tests, Docker, and continuous integration.

> Portuguese setup and Git instructions: [docs/GUIDE.pt-BR.md](docs/GUIDE.pt-BR.md)

## Main features

- Complete CRUD with `GET`, `POST`, `PUT`, `PATCH`, and `DELETE`
- Application factory and modular blueprints
- SQLite by default, with support for other SQLAlchemy databases
- Alembic migrations through Flask-Migrate
- Consistent JSON responses and error handling
- Payload validation and unknown-field rejection
- Search, status and priority filters
- Pagination and configurable sorting
- Automatic completion timestamp management
- Pytest integration tests with more than 90% coverage
- Ruff linting and formatting
- GitHub Actions CI workflow
- Docker and Docker Compose support
- VS Code debug, testing, and task configurations

## Technology stack

- Python 3.11+
- Flask 3
- Flask-SQLAlchemy
- Flask-Migrate / Alembic
- Pytest and pytest-cov
- Ruff
- Gunicorn
- Docker

## Project structure

```text
.
├── app/
│   ├── health/              # Health-check endpoint
│   ├── tasks/               # Task domain, routes, service and repository
│   ├── commands.py          # Custom Flask CLI commands
│   ├── config.py            # Runtime configuration
│   ├── errors.py            # JSON error handlers
│   ├── extensions.py        # SQLAlchemy and migration instances
│   └── __init__.py          # Application factory
├── migrations/              # Database migration history
├── tests/                   # Integration tests
├── .github/workflows/ci.yml # Continuous integration
├── .vscode/                 # VS Code configuration
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── run.py                   # Development entry point
└── wsgi.py                  # Production WSGI entry point
```

## Quick start

### Windows PowerShell

```powershell
git clone https://github.com/moisesneivert/Flask-Tasks-Crud-Api.git
cd Flask-Tasks-Crud-Api

py -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements-dev.txt
Copy-Item .env.example .env

flask --app run.py db upgrade
flask --app run.py seed
python run.py
```

### Linux or macOS

```bash
git clone https://github.com/moisesneivert/Flask-Tasks-Crud-Api.git
cd Flask-Tasks-Crud-Api

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements-dev.txt
cp .env.example .env

flask --app run.py db upgrade
flask --app run.py seed
python run.py
```

The API will be available at `http://127.0.0.1:5000`.

## Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | API information |
| `GET` | `/health` | Health check |
| `GET` | `/api/v1/tasks` | List tasks |
| `GET` | `/api/v1/tasks/{id}` | Get a task by ID |
| `POST` | `/api/v1/tasks` | Create a task |
| `PUT` | `/api/v1/tasks/{id}` | Fully replace a task |
| `PATCH` | `/api/v1/tasks/{id}` | Partially update a task |
| `DELETE` | `/api/v1/tasks/{id}` | Delete a task |

## Task fields

| Field | Type | Required on POST/PUT | Accepted values |
|---|---|---:|---|
| `title` | string | Yes | 3 to 120 characters |
| `description` | string or null | No | Up to 1,000 characters |
| `status` | string | No | `pending`, `in_progress`, `completed` |
| `priority` | string | No | `low`, `medium`, `high` |
| `due_date` | string or null | No | ISO date: `YYYY-MM-DD` |

Fields such as `id`, `created_at`, `updated_at`, and `completed_at` are managed by the API.

## Create a task

```bash
curl --request POST http://127.0.0.1:5000/api/v1/tasks \
  --header "Content-Type: application/json" \
  --data '{
    "title": "Write integration tests",
    "description": "Cover every task endpoint.",
    "status": "in_progress",
    "priority": "high",
    "due_date": "2026-07-15"
  }'
```

Example response:

```json
{
  "data": {
    "id": 1,
    "title": "Write integration tests",
    "description": "Cover every task endpoint.",
    "status": "in_progress",
    "priority": "high",
    "due_date": "2026-07-15",
    "completed_at": null,
    "created_at": "2026-06-30T18:00:00Z",
    "updated_at": "2026-06-30T18:00:00Z"
  }
}
```

## List, filter, search, and sort

Available query parameters:

| Parameter | Default | Description |
|---|---:|---|
| `page` | `1` | Page number |
| `per_page` | `20` | Items per page, maximum 100 |
| `status` | — | Filter by task status |
| `priority` | — | Filter by task priority |
| `q` | — | Search in title and description |
| `sort_by` | `created_at` | `id`, `title`, `status`, `priority`, `due_date`, `created_at`, or `updated_at` |
| `order` | `desc` | `asc` or `desc` |

Example:

```text
GET /api/v1/tasks?status=pending&priority=high&q=python&page=1&per_page=10&sort_by=due_date&order=asc
```

## PUT versus PATCH

`PUT` fully replaces all editable fields. Fields not provided return to their defaults or to `null`, so `title` is required.

`PATCH` changes only the fields sent in the request and requires at least one editable field.

## Error format

```json
{
  "error": {
    "code": "validation_error",
    "message": "The request data is invalid.",
    "details": {
      "title": "This field is required."
    }
  }
}
```

## Quality checks

```bash
ruff check .
ruff format --check .
pytest
```

To apply formatting automatically:

```bash
ruff check . --fix
ruff format .
```

## Database migrations

Apply all migrations:

```bash
flask --app run.py db upgrade
```

After changing a model:

```bash
flask --app run.py db migrate -m "describe the model change"
flask --app run.py db upgrade
```

Revert the latest migration:

```bash
flask --app run.py db downgrade
```

## Sample data

```bash
flask --app run.py seed
```

The command only inserts sample tasks when the tasks table is empty.

## Docker

```bash
docker compose up --build
```

The container applies pending migrations before starting Gunicorn. SQLite data is persisted in a named Docker volume.

## Environment variables

Copy `.env.example` to `.env`. The `.env` file is ignored by Git.

| Variable | Default | Description |
|---|---|---|
| `FLASK_DEBUG` | `1` | Enables local debug mode when using `python run.py` |
| `HOST` | `127.0.0.1` | Development server host |
| `PORT` | `5000` | Development server port |
| `DATABASE_URL` | SQLite | SQLAlchemy database connection URI |

For a database other than SQLite, install its Python DBAPI driver. For example, PostgreSQL with the URI `postgresql+psycopg://...` requires `pip install "psycopg[binary]"`.

Never commit real passwords, tokens, or production connection strings.

## Postman

Import [docs/Flask-Tasks-CRUD-API.postman_collection.json](docs/Flask-Tasks-CRUD-API.postman_collection.json) into Postman. The collection uses the variable `base_url`, which defaults to `http://127.0.0.1:5000`.

## License

Distributed under the MIT License. See [LICENSE](LICENSE).
