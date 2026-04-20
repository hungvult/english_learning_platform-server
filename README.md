# English Learning Platform — Server

This is the backend for the **English Learning Platform**, built with **FastAPI** and **SQLModel**. It leverages **Microsoft SQL Server** for data persistence and **JWT** for secure authentication and RBAC (Role-Based Access Control).

## Prerequisites
- **Python**: 3.10+ (Recommended: 3.13)
- **Database**: SQL Server 2022 instance.
- **Driver**: Microsoft ODBC Driver 18 for SQL Server.

## Environment Variables
The application requires a `.env` file in the `server/` directory:

| Variable                      | Description                         | Example                                                                                                                     |
| ----------------------------- | ----------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `DATABASE_URL`                | SQL Server connection string        | `mssql+pyodbc://sa:Password@localhost:1433/EnglishLearning?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes` |
| `SECRET_KEY`                  | JWT signing secret                  | (Your random secret string)                                                                                                 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime (default 1440 = 24h) | `1440`                                                                                                                      |

## Installation & Running Locally

1. Create a virtual environment: `python -m venv venv`
2. Activate venv & install dependencies: `source venv/bin/activate && pip install -r requirements.txt`
3. Run with uvicorn: `uvicorn app.main:app --reload`

## Project Structure

- **`app/main.py`**: Entry point and FastAPI configuration.
- **`app/api/v1/`**: API Route documentation and versioned router.
  - **`endpoints/admin/`**: High-privilege routes for CMS operations.
- **`app/models/`**: SQLModel table definitions (e.g., `Exercise`, `Lesson`, `Unit` with `order_index`).
- **`app/schemas/`**: Pydantic models for request/response validation (Admin/Client subsets).
- **`app/services/`**: Core business logic: XP calculation, streaks, and validation services.
- **`app/core/`**: Security configuration, database engine, and global settings.
- **`static/audio/`**: Directory for serving exercise audio assets.

## API Endpoints (Core)

| Method | Path                           | Auth | Description                   |
| ------ | ------------------------------ | ---- | ----------------------------- |
| POST   | `/api/v1/auth/login`           | No   | Get JWT token                 |
| GET    | `/api/v1/courses/{id}`         | No   | Get curriculum hierarchy      |
| GET    | `/api/v1/lessons/{id}/payload` | Yes  | Get full exercise data        |
| POST   | `/api/v1/lessons/{id}/submit`  | Yes  | Progress & XP submission      |

## Admin Endpoints (Reordering)

| Method | Path                                 | Description                                 |
| ------ | ------------------------------------ | ------------------------------------------- |
| POST   | `/api/v1/admin/units/swap-order`     | Atomic swap of `order_index` for two units  |
| POST   | `/api/v1/admin/lessons/swap-order`   | Atomic swap of `order_index` for two lessons|
| POST   | `/api/v1/admin/exercises/swap-order` | Atomic swap of `order_index` for exercises  |

## Database Migration
Standalone SQL script: `scripts/add_exercise_order_index.sql`.
Used to add sequencing support to legacy tables.
