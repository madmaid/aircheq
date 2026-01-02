## BUILD
FROM python:3.9-slim-bookworm as base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

## install dependencies with apt
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
    curl build-essential xz-utils; \
    rm -rf /var/lib/apt/lists/*

## install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

## ffmpeg
COPY --from=mwader/static-ffmpeg:6.0 /ffmpeg /opt

WORKDIR /opt/app
COPY pyproject.toml ./
COPY uv.lock ./
RUN uv sync --frozen --no-dev

## RUN operator
FROM python:3.9-slim-bookworm as operator_stage
COPY --from=base /opt/app/.venv /opt/app/.venv
COPY --from=base /opt/ffmpeg /usr/bin/ffmpeg
COPY ./aircheq /opt/app/aircheq
COPY ./alembic.ini /opt/app/alembic.ini
COPY ./migration /opt/app/migration
RUN mkdir /opt/app/aircheq_config
WORKDIR /opt/app
CMD ["/opt/app/.venv/bin/python", "-m", "aircheq", "--config-dir=/opt/app/aircheq_config/"]

## RUN web
FROM python:3.9-slim-bookworm as web_stage
COPY --from=base /opt/app/.venv /opt/app/.venv
COPY ./aircheq /opt/app/aircheq
COPY ./alembic.ini /opt/app/alembic.ini
COPY ./migration /opt/app/migration
RUN mkdir /opt/app/aircheq_config
WORKDIR /opt/app
CMD ["/opt/app/.venv/bin/python", "-m", "aircheq.web", "--config-dir=/opt/app/aircheq_config/"]