########### BASE STAGE ###########
FROM python:2.7.13-alpine AS base

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONWARNINGS='ignore::DeprecationWarning'

# copy base requirements
COPY ./requirements.txt /app/

# install base dependencies
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    libxml2-dev \
    libxslt-dev \
    python-dev \
    && apk add --no-cache py-lxml mariadb-dev \
    && pip install --upgrade pip setuptools && pip install --no-cache-dir -r /app/requirements.txt \
    && apk del .build-deps 

EXPOSE 8000

WORKDIR /app


########### DEV STAGE ###########
FROM base AS dev

# copy dev requirements
COPY ./requirements-dev.txt /app/

# install dev dependencies
RUN pip install --no-cache-dir -r /app/requirements-dev.txt


########### PRODUCTION STAGE ###########
FROM base AS prod

# create directory for collectstatic command
RUN mkdir /app/static_files

# set local user
USER appuser

# copy aplication files to image
COPY ./bireme/ /app/
