FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc python3-dev libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry without creating virtualenv
RUN pip install --upgrade pip && \
    pip install poetry gunicorn

# Copy dependency files first for caching
COPY ./app/pyproject.toml ./app/poetry.lock* ./

# Install only dependencies (skip project installation)
RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-root --no-interaction --no-ansi

# Copy application code
COPY ./app /app
COPY ./app/.env /app/.env

# Create empty README if missing (temporary solution)
RUN touch README.md

# Install the project (if needed)
# RUN poetry install --no-interaction --no-ansi

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "core.wsgi:application"]