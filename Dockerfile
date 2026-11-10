FROM python:3.13.9-slim@sha256:326df678c20c78d465db501563f3492d17c42a4afe33a1f2bf5406a1d56b0e86

RUN pip install --no-cache-dir uv==0.9.5
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev
COPY src ./src
COPY alembic.ini ./
COPY tests ./tests
ENV PATH="/app/.venv/bin:$PATH" TZ=UTC
EXPOSE 8000
