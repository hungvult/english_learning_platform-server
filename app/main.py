from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
import os

# Import all models so SQLModel metadata is populated
import app.models  # noqa: F401
from app.api.v1.router import api_router

# ---------------------------------------------------------------------------
# Tag metadata — controls ordering and descriptions in Swagger UI
# ---------------------------------------------------------------------------
TAGS_METADATA = [
    {"name": "Health",      "description": "Service liveness check."},
    {"name": "Auth",        "description": "Register and obtain JWT tokens."},
    {"name": "Users",       "description": "Current user profile operations."},
    {"name": "Courses",     "description": "Browse available courses and their content tree."},
    {"name": "Lessons",     "description": "Pre-fetch lesson payloads and submit completions."},
    {"name": "Exercises",   "description": "Exercise catalogue."},
    {
        "name": "Admin — Users",
        "description": "**Admin only.** Full CRUD on user accounts, including role management.",
    },
    {
        "name": "Admin — Courses",
        "description": "**Admin only.** Create, update, and delete courses.",
    },
    {
        "name": "Admin — Units",
        "description": "**Admin only.** Create, update, and delete units within courses.",
    },
    {
        "name": "Admin — Lessons",
        "description": "**Admin only.** Create, update, and delete lessons within units.",
    },
    {
        "name": "Admin — Exercises",
        "description": "**Admin only.** Create, update, and delete exercises within lessons.",
    },
]

app = FastAPI(
    title="English Learning Platform API",
    version="1.0.0",
    description=(
        "REST API for the **English Learning Platform**.\n\n"
        "## Authentication\n"
        "Most endpoints require a **Bearer JWT** token.\n"
        "1. Call `POST /api/v1/auth/register` or `POST /api/v1/auth/login` to obtain a token.\n"
        "2. Click **Authorize** (🔒) and paste the token.\n\n"
        "## Admin access\n"
        "Endpoints under the **Admin —** groups require `is_admin = true` on the user account."
    ),
    openapi_tags=TAGS_METADATA,
    # Keep Swagger UI and ReDoc at their default paths
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------
static_dirs = ["audio", "images"]
for dir_name in static_dirs:
    dir_path = os.path.join(os.path.dirname(__file__), "static", dir_name)
    os.makedirs(dir_path, exist_ok=True)

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")),
    name="static",
)

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "english-learning-platform"}


# ---------------------------------------------------------------------------
# Custom OpenAPI schema — injects HTTP Bearer security scheme so Swagger UI
# shows the Authorize 🔒 button and persists the token across requests.
# ---------------------------------------------------------------------------
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        tags=TAGS_METADATA,
        routes=app.routes,
    )

    # Add Bearer security scheme
    schema.setdefault("components", {})
    schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Paste your JWT token (without the 'Bearer ' prefix).",
        }
    }

    # Apply security globally so every endpoint shows the lock icon
    schema["security"] = [{"BearerAuth": []}]

    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi  # type: ignore[method-assign]
