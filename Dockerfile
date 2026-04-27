FROM python:3.13-slim

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml uv.lock* ./
RUN uv sync --locked

COPY . .

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000