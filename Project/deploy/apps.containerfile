ARG APP_NAME

## local_packages
FROM scratch AS local_packages
WORKDIR /app/packages
WORKDIR /app

# Common packages across all apps
COPY ./packages/nonce ./packages/nonce/
COPY ./packages/secure_endpoints ./packages/secure_endpoints/
COPY ./packages/utils ./packages/utils/

## authentication_server_local_packages
FROM local_packages AS authentication_server_local_packages
COPY ./packages/cert_manager ./packages/cert_manager/

## authorization_server_local_packages
FROM local_packages AS authorization_server_local_packages
COPY ./packages/cert_manager ./packages/cert_manager/

## resource_server_local_packages
FROM local_packages AS resource_server_local_packages

## web_server_local_packages
FROM local_packages AS web_server_local_packages

## project_local_packages
FROM ${APP_NAME:?}_local_packages AS project_local_packages



## base
FROM python:3.12-alpine3.21 AS base

ENV PYTHONBUFFERED=1

# Create non-root user for installs
RUN adduser -D runner
USER runner

# Use virtual environment for all following commands
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"



## dependencies
FROM base AS dependencies
ARG APP_NAME

# Create pip cache
WORKDIR /opt/cache/pip
ENV PIP_CACHE_DIR=/opt/cache/pip

# Create poetry cache
WORKDIR /opt/cache/poetry
ENV POETRY_CACHE_DIR=/opt/cache/poetry
ENV POETRY_VIRTUALENVS_CREATE=false

# Create virtual environment where all dependencies will be installed
WORKDIR /opt/venv
RUN python -m venv .

# Install poetry
WORKDIR /app
COPY poetry-requirements.txt ./

RUN --mount=type=cache,target=/usr/cache/pip \
    pip install -r poetry-requirements.txt

# Copy project file and install dependencies
COPY ./apps/${APP_NAME:?}/pyproject.toml ./apps/${APP_NAME:?}/poetry.lock ./apps/${APP_NAME:?}/
RUN poetry install --no-directory -C apps/${APP_NAME:?}



## project
FROM base AS project
ARG APP_NAME

# Directory to scaffold and install the app
WORKDIR /app

COPY --chown=runner:runner --from=dependencies /opt/venv /opt/venv
COPY --chown=runner:runner --from=project_local_packages /app/packages ./packages
COPY --chown=runner:runner ./apps/${APP_NAME:?}/ ./apps/${APP_NAME:?}/

RUN poetry install --no-cache -C apps/${APP_NAME:?}



## runner
FROM project AS runner
ARG APP_NAME
ARG APP_PORT=5000

ENV APP_NAME=${APP_NAME:?}
ENV APP_PORT=${APP_PORT}

EXPOSE ${APP_PORT}

WORKDIR /app/apps/${APP_NAME:?}

## runner_dev
FROM runner AS runner_dev

ENV ENVIRONMENT=development

COPY ./deploy/apps/entrypoint_dev.sh /entrypoint.sh
CMD [ "/entrypoint.sh" ]

## runner_prod
FROM runner AS runner_prod

ENV ENVIRONMENT=production

COPY ./deploy/apps/entrypoint_prod.sh /entrypoint.sh
CMD [ "/entrypoint.sh" ]
