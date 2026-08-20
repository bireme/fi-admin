#!/bin/bash

# Makefile for managing Docker Compose environments for fi-admin application
IMAGE_NAME=bireme/fi-admin
BASE_VERSION := $(shell git describe --tags --long --always \
	| sed 's/-g[[:xdigit:]]\{7,\}$$//' \
	| sed 's/-/./g')

BRANCH_NAME := $(shell git branch --show-current \
	| sed 's#[^a-zA-Z0-9._-]#-#g')

APP_VERSION ?= $(strip $(if $(filter main,$(BRANCH_NAME)),\
	$(BASE_VERSION),\
	$(BASE_VERSION)-$(BRANCH_NAME)))

TAG_LATEST=$(IMAGE_NAME):latest

COMPOSE_FILE_DEV=docker-compose-dev.yml
COMPOSE_FILE_API=docker-compose-api.yml

## variable used in docker-compose for tag the build image
export IMAGE_TAG=$(IMAGE_NAME):$(APP_VERSION)

## variable used in docker-compose as build arg (baked into the image)
export APP_VERSION

tag:
	@echo "IMAGE TAG:" $(IMAGE_TAG)

## docker-compose desenvolvimento
dev_build:
	@docker compose -f $(COMPOSE_FILE_DEV) build

dev_build_no_cache:
	@docker compose -f $(COMPOSE_FILE_DEV) build --no-cache

dev_up:
	@docker compose -f $(COMPOSE_FILE_DEV) up -d

dev_run:
	@docker compose -f $(COMPOSE_FILE_DEV) up

dev_logs:
	@docker compose -f $(COMPOSE_FILE_DEV) logs -f

dev_stop:
	@docker compose -f $(COMPOSE_FILE_DEV) stop

dev_down:
	@docker compose -f $(COMPOSE_FILE_DEV) down

dev_ps:
	@docker compose -f $(COMPOSE_FILE_DEV) ps

dev_rm:
	@docker compose -f $(COMPOSE_FILE_DEV) rm -f

dev_sh:
	@docker compose -f $(COMPOSE_FILE_DEV) exec fi_admin sh

dev_exec:
	@docker compose -f $(COMPOSE_FILE_DEV) exec -T fi_admin $(cmd)

dev_makemigrations:
	@docker compose -f $(COMPOSE_FILE_DEV) exec fi_admin python manage.py makemigrations $(app)

dev_migrate:
	@docker compose -f $(COMPOSE_FILE_DEV) exec fi_admin python manage.py migrate $(app)

dev_check:
	@docker compose -f $(COMPOSE_FILE_DEV) exec -T fi_admin python manage.py check

dev_test:
	@docker compose -f $(COMPOSE_FILE_DEV) exec fi_admin sh run_tests.sh

dev_test_app:
	@docker compose -f $(COMPOSE_FILE_DEV) exec -T fi_admin python -W ignore manage.py test -v 1 $(app)

dev_test_coverage:
	@docker compose -f $(COMPOSE_FILE_DEV) exec -T fi_admin sh run_coverage.sh

dev_update_translations:
	@docker compose -f $(COMPOSE_FILE_DEV) exec fi_admin sh -c "apk add --no-cache gettext && python manage.py makemessages --all"

dev_loaddata:
	@docker compose -f $(COMPOSE_FILE_DEV) exec -T fi_admin python manage.py loaddata $(import_file)

## docker-compose API
api_build:
	@docker compose -f $(COMPOSE_FILE_API) build
	@docker tag $(IMAGE_TAG) $(TAG_LATEST)

api_build_no_cache:
	@docker compose -f $(COMPOSE_FILE_API) build --no-cache
	@docker tag $(IMAGE_TAG) $(TAG_LATEST)

api_up:
	@docker compose -f $(COMPOSE_FILE_API) up -d

api_run:
	@docker compose -f $(COMPOSE_FILE_API) up

api_logs:
	@docker compose -f $(COMPOSE_FILE_API) logs -f

api_stop:
	@docker compose -f $(COMPOSE_FILE_API) stop

api_ps:
	@docker compose -f $(COMPOSE_FILE_API) ps

api_rm:
	@docker compose -f $(COMPOSE_FILE_API) rm -f

api_rollback:
	@echo '*** ROLLBACK TO VERSION $(APP_VERSION) ***'
	@docker compose -f $(COMPOSE_FILE_API) stop
	@docker compose -f $(COMPOSE_FILE_API) up -d

api_exec_shell:
	@docker compose -f $(COMPOSE_FILE_API) exec fi_admin_api sh

api_exec_collectstatic:
	@docker compose -f $(COMPOSE_FILE_API) exec -T fi_admin_api python manage.py collectstatic --noinput

api_exec_webserver:
	@docker compose -f $(COMPOSE_FILE_API) exec webserver sh

api_make_test:
	@docker compose -f $(COMPOSE_FILE_API) exec -T fi_admin_api make test

## docker-compose prod
prod_build:
	@docker compose build
	@docker tag $(IMAGE_TAG) $(TAG_LATEST)

prod_build_no_cache:
	@docker compose build --no-cache
	@docker tag $(IMAGE_TAG) $(TAG_LATEST)

prod_up:
	@docker compose up -d

prod_run:
	@docker compose up

prod_logs:
	@docker compose logs -f

prod_stop:
	@docker compose stop

prod_ps:
	@docker compose ps

prod_rm:
	@docker compose rm -f

prod_down:
	@docker compose down

prod_list_images:
	@docker images $(IMAGE_NAME}

prod_rollback:
	@echo '*** ROLLBACK TO VERSION $(APP_VERSION) ***'
	@docker compose stop
	@docker compose up -d

prod_exec_shell:
	@docker compose exec fi_admin sh

prod_exec_collectstatic:
	@docker compose exec -T fi_admin python manage.py collectstatic --noinput

prod_loaddata:
	@docker compose exec -T fi_admin python manage.py loaddata $(import_file)

prod_exec_webserver:
	@docker compose exec webserver sh

prod_make_test:
	@docker compose exec -T fi_admin make test

# import data to fi-admin
import:
	@docker compose exec -T fi_admin sh -c "cd /app/proc/import && sh import2FIAdmin.sh"

# import data to fi-admin using prod-db.env
import2prod:
	@docker compose exec -T fi_admin sh -c "set -a && . /app/proc/import/prod-db.env && set +a && cd /app/proc/import && sh import2FIAdmin.sh"
