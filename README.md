# English Learning Platform — Server

FastAPI backend. Python 3.13+, SQL Server, JWT auth.

## Prerequisites

- Python 3.10+
- SQL Server instance (local or remote)
- Microsoft ODBC Driver 18 for SQL Server

## `.env` fields

| Variable                      | Description                         | Example                                                                                                                     |
| ----------------------------- | ----------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `DATABASE_URL`                | SQL Server connection string        | `mssql+pyodbc://sa:Password@localhost:1433/EnglishLearning?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes` |
| `SECRET_KEY`                  | JWT signing secret                  | any long random string                                                                                                      |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime (default 1440 = 24h) | `1440`                                                                                                                      |

## Docker Development

### Running with Hot Reload

To start the development server with automatic reloading when code changes:

```bash
docker compose up dev
```

- Source code in `./app` is bind-mounted into the container.
- Changes are reflected immediately.

### Running Production Image

To run the lean, security-hardened production image:

```bash
docker compose up backend
```

### Rebuilding

If you change `requirements.txt` or the `Dockerfile`:

```bash
docker compose build
```

## Project Structure

```text
app/
├── api/v1/endpoints/   # Route handlers (auth, users, courses, lessons, exercises)
├── core/               # Config, database engine, JWT/bcrypt security
├── models/             # SQLModel table definitions
├── repositories/       # Data access layer
├── schemas/            # Pydantic request/response schemas
├── services/           # Business logic (XP, streak, auth)
├── static/audio/       # Audio files for listening exercises
└── main.py             # App entry point
```

## API Endpoints

| Method | Path                           | Auth | Description               |
| ------ | ------------------------------ | ---- | ------------------------- |
| POST   | `/api/v1/auth/register`        | No   | Register and get JWT      |
| POST   | `/api/v1/auth/login`           | No   | Login and get JWT         |
| GET    | `/api/v1/users/me`             | Yes  | Current user profile      |
| PATCH  | `/api/v1/users/me`             | Yes  | Update profile            |
| GET    | `/api/v1/courses/`             | No   | List courses              |
| GET    | `/api/v1/courses/{id}`         | No   | Course with units/lessons |
| GET    | `/api/v1/lessons/{id}/payload` | Yes  | Full exercise payload     |
| POST   | `/api/v1/lessons/{id}/submit`  | Yes  | Submit lesson completion  |

## Default Password

All seeded users use `abc123` as the default password.
