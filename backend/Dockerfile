FROM python:3.13 as builder
RUN pip install poetry==2.1.2
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --without dev,test --no-root

FROM python:3.13-slim as runtime
RUN apt-get update && \
    apt-get install -y libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*
ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"
COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY . /code/
WORKDIR /code
