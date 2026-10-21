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

# copy base requirements
COPY ./requirements.txt /app/

# install base dependencies
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    libxml2-dev \
    libxslt-dev \
    python3-dev \
    pkgconf \
    && apk add --no-cache mariadb-dev \
    # setuptools<81: deform 3.0.1 imports pkg_resources, removed in setuptools 81
    && pip install --upgrade pip "setuptools<81" && pip install --no-cache-dir -r /app/requirements.txt \
    && apk del .build-deps

EXPOSE 8000

WORKDIR /app


########### DEV STAGE ###########
FROM base AS dev

# install dev system dependencies
RUN apk add --no-cache make

# copy dev requirements
COPY ./requirements-dev.txt /app/

# install dev dependencies
RUN pip install --no-cache-dir -r /app/requirements-dev.txt


########### PRODUCTION STAGE ###########
FROM base AS prod

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
