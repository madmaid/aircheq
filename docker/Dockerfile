## BUILD
FROM python:3.9-slim-buster as base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

## apt
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        curl build-essential xz-utils gosu; \
    rm -rf /var/lib/apt/lists/*; \
    gosu nobody true

## ffmpeg
RUN curl -Lo /tmp/ffmpeg.tar.gz "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"; \
    tar -C /tmp -xf /tmp/ffmpeg.tar.gz; \
    mv /tmp/ffmpeg-*-amd64-static/ffmpeg /opt; \
    rm -rf /tmp/ffmpeg*

WORKDIR /opt/app
RUN pip3 install poetry
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-dev


## RUN operator
FROM base as operator_stage

COPY --from=base /opt/app/.venv /opt/app/.venv
COPY --from=base /opt/ffmpeg /usr/bin/ffmpeg
COPY ./aircheq /opt/app/aircheq
COPY ./alembic.ini  /opt/app/alembic.ini
COPY ./migration /opt/app/migration

WORKDIR /opt/app


COPY ./docker/entrypoint.sh /opt/app/entrypoint.sh
ENTRYPOINT ["/opt/app/entrypoint.sh"]
CMD ["gosu", "aircheq", "bash", "-c", "cd /opt/app && source ./.venv/bin/activate && python -m aircheq"]

## RUN web
FROM base as web_stage

COPY --from=base /opt/app/.venv /opt/app/.venv
COPY ./aircheq /opt/app/aircheq
COPY ./alembic.ini  /opt/app/alembic.ini
COPY ./migration /opt/app/migration

WORKDIR /opt/app

COPY ./docker/entrypoint.sh /opt/app/entrypoint.sh
ENTRYPOINT ["/opt/app/entrypoint.sh"]
CMD ["gosu", "aircheq", "bash", "-c", \ 
    "cd /opt/app && \
    source ./.venv/bin/activate && \
    FLASK_APP='aircheq.web.__main__.py' \
    flask run --host=0.0.0.0 --port=5000"]
    # python -m aircheq.web"]

# CMD gosu aircheq bash -c "\
    # cd /opt/app && \
    # source ./.venv/bin/activate && \
    # FLASK_APP='aircheq.web.__main__.py' flask run --host=localhost"
