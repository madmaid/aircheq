## BUILD
FROM python:3.9-slim-bookworm as base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

## install ffmpeg dependencies with apt
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        curl build-essential xz-utils; \
    rm -rf /var/lib/apt/lists/*; 

## ffmpeg
RUN curl -Lo /tmp/ffmpeg.tar.gz "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"; \
    tar -C /tmp -xf /tmp/ffmpeg.tar.gz; \
    mv /tmp/ffmpeg-*-amd64-static/ffmpeg /opt; \
    rm -rf /tmp/ffmpeg*

WORKDIR /opt/app
RUN pip3 install --no-cache-dir poetry
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-dev


## RUN operator
FROM base as operator_stage

COPY --from=base /opt/app/.venv /opt/app/.venv
COPY --from=base /opt/ffmpeg /usr/bin/ffmpeg
COPY ./aircheq /opt/app/aircheq
COPY ./alembic.ini  /opt/app/alembic.ini
COPY ./migration /opt/app/migration
RUN mkdir /opt/app/aircheq_config

WORKDIR /opt/app
CMD ["bash", "-c", "source /opt/app/.venv/bin/activate && python -m aircheq --config-dir=/opt/app/aircheq_config/"]

## RUN web
FROM base as web_stage

COPY --from=base /opt/app/.venv /opt/app/.venv
COPY ./aircheq /opt/app/aircheq
COPY ./alembic.ini  /opt/app/alembic.ini
COPY ./migration /opt/app/migration
RUN mkdir /opt/app/aircheq_config

WORKDIR /opt/app
CMD ["bash", "-c", "source /opt/app/.venv/bin/activate && python -m aircheq.web --config-dir=/opt/app/aircheq_config/"]
