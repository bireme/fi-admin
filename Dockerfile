# python version of the base image (override with --build-arg, e.g. make dev_test_py)
ARG PYTHON_VERSION=3.14

########### BASE STAGE ###########
FROM python:${PYTHON_VERSION}-alpine AS base

# application version (informed by the Makefile at build time)
ARG APP_VERSION=unknown

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_VERSION=${APP_VERSION}

# uv package manager (dependencies in src/pyproject.toml + src/uv.lock)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# install runtime system dependencies
RUN apk add --no-cache mariadb-dev

EXPOSE 8000

WORKDIR /app


########### DEV STAGE ###########
FROM base AS dev

# uv run syncs /app/.venv (src/.venv on the host) from the lock before running
ENV UV_FROZEN=1
# the uv cache and the bind-mounted venv are on different filesystems
ENV UV_LINK_MODE=copy

# install dev system dependencies; build deps stay installed because the venv is
# created at runtime inside the container (compiles mysqlclient and lxml)
RUN apk add --no-cache \
    make \
    gcc \
    musl-dev \
    libxml2-dev \
    libxslt-dev \
    python3-dev \
    pkgconf


########### PRODUCTION STAGE ###########
FROM base AS prod

# uv run uses the venv baked into the image as is
ENV UV_NO_SYNC=1

# copy dependency files
COPY ./src/pyproject.toml ./src/uv.lock /app/

# install python dependencies into /app/.venv
RUN --mount=type=cache,target=/root/.cache/uv \
    apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    libxml2-dev \
    libxslt-dev \
    python3-dev \
    pkgconf \
    && UV_LINK_MODE=copy uv sync --frozen --no-dev --no-install-project \
    && apk del .build-deps

# copy crontab scripts
COPY ./conf/crontab/daily/* /etc/periodic/daily/
COPY ./conf/crontab/weekly/* /etc/periodic/weekly/
COPY ./conf/crontab/monthly/* /etc/periodic/monthly/

RUN chmod +x /etc/periodic/daily/*
RUN chmod +x /etc/periodic/weekly/*
RUN chmod +x /etc/periodic/monthly/*

# create a app user
RUN addgroup -S appuser && adduser -S appuser -G appuser

# create directory for collectstatic command
RUN mkdir /app/static_files && chown appuser:appuser /app/static_files

# copy project
COPY --chown=appuser:appuser ./src/ /app/

# change to the app user
USER appuser
