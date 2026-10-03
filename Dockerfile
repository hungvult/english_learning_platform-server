# ── Stage 1: builder ──────────────────────────────────────────────────────────
FROM python:3.12-slim-bookworm AS builder

WORKDIR /build

# Install build tools and ODBC development headers needed for compiling pyodbc
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment to isolate dependencies cleanly
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install -r requirements.txt


# ── Stage 2: runtime ──────────────────────────────────────────────────────────
FROM python:3.12-slim-bookworm AS runtime

LABEL maintainer="english-learning-platform"
LABEL org.opencontainers.image.description="English Learning Platform - FastAPI backend"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Install Microsoft ODBC runtime driver and unixodbc, then purge curl & gnupg to keep image lean
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        gnupg \
        unixodbc \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && curl -fsSL https://packages.microsoft.com/config/debian/12/prod.list | tee /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 \
    && apt-get purge -y --auto-remove curl gnupg \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Create a non-root system user and group
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --ingroup appgroup appuser

WORKDIR /app

# Ensure static directories exist with correct permissions for upload persistence
RUN mkdir -p /app/app/static/audio /app/app/static/images && \
    chown -R appuser:appgroup /app

# Copy application source
COPY --chown=appuser:appgroup app/ ./app/

USER appuser

EXPOSE 8000

# Built-in lightweight health check using python standard library (no curl needed)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/')" || exit 1

# Workers = 1 keeps connection pool behaviour predictable with pyodbc
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]


# ── Stage 3: development (hot-reload) ─────────────────────────────────────────
FROM runtime AS dev

# In development, keep appuser so container file creation does not pollute host with root ownership
USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
