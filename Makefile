#!/bin/bash

# Makefile for managing Docker Compose environments for fi-admin application
IMAGE_NAME=bireme/fi-admin
APP_VERSION?=$(shell git describe --tags --long --always | sed 's/-g[a-z0-9]\{7\}//' | sed 's/-/\./')
TAG_LATEST=$(IMAGE_NAME):latest

COMPOSE_FILE_DEV=docker-compose-dev.yml
COMPOSE_FILE_API=docker-compose-api.yml

# Use 'docker compose' if available (Docker 20.10+), otherwise fall back to 'docker-compose'
DOCKER_COMPOSE := $(shell if docker compose version >/dev/null 2>&1; then echo "docker compose"; elif command -v docker-compose >/dev/null 2>&1; then echo "docker-compose"; else echo "docker compose"; fi)

## variable used in docker-compose for tag the build image
export IMAGE_TAG=$(IMAGE_NAME):$(APP_VERSION)

tag:
	@echo "IMAGE TAG:" $(IMAGE_TAG)


## docker-compose desenvolvimento
dev_build:
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FILE_DEV) build

dev_build_no_cache:
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FILE_DEV) build --no-cache

dev_up:
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FILE_DEV) up -d

dev_run:
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FILE_DEV) up

dev_logs:
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FILE_DEV) logs -f

dev_stop:
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FILE_DEV) stop

dev_down:
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FILE_DEV) down

dev_ps:
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FILE_DEV) ps

dev_rm:
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FILE_DEV) rm -f

dev_sh:
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FILE_DEV) exec fi_admin sh

dev_makemigrations:
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FILE_DEV) exec fi_admin python manage.py makemigrations $(app)

dev_migrate:
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FILE_DEV) exec fi_admin python manage.py migrate $(app)

dev_test:
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FILE_DEV) exec fi_admin sh run_tests.sh

dev_test_app:
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FILE_DEV) exec -T fi_admin python -W ignore manage.py test -v 1 $(app)

dev_test_coverage:
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FILE_DEV) exec -T fi_admin sh run_coverage.sh

dev_update_translations:
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FILE_DEV) exec fi_admin sh -c "apk add --no-cache gettext && python manage.py makemessages --all"

dev_loaddata:
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FILE_DEV) exec -T fi_admin python manage.py loaddata $(import_file)

## docker-compose API
api_build:
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FILE_API) --compatibility build
	@docker tag $(IMAGE_TAG) $(TAG_LATEST)

api_build_no_cache:
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FILE_API) --compatibility build --no-cache
	@docker tag $(IMAGE_TAG) $(TAG_LATEST)

api_up:
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FILE_API) --compatibility up -d

api_run:
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FILE_API) --compatibility up

api_logs:
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FILE_API) --compatibility logs -f

api_stop:
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FILE_API) --compatibility stop

api_ps:
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FILE_API) --compatibility ps

api_rm:
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FILE_API) --compatibility rm -f

api_rollback:
	@echo '*** ROLLBACK TO VERSION $(APP_VERSION) ***'
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FILE_API) --compatibility stop
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FILE_API) --compatibility up -d

api_exec_shell:
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FILE_API) --compatibility exec fi_admin_api sh

api_exec_collectstatic:
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FILE_API) --compatibility exec -T fi_admin_api python manage.py collectstatic --noinput

api_exec_webserver:
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FILE_API) --compatibility exec webserver sh

api_make_test:
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FILE_API) --compatibility exec -T fi_admin_api make test

## docker-compose prod
prod_build:
	@$(DOCKER_COMPOSE) --compatibility build
	@docker tag $(IMAGE_TAG) $(TAG_LATEST)

prod_build_no_cache:
	@$(DOCKER_COMPOSE) --compatibility build --no-cache
	@docker tag $(IMAGE_TAG) $(TAG_LATEST)

prod_up:
	@$(DOCKER_COMPOSE) --compatibility up -d

prod_run:
	@$(DOCKER_COMPOSE) --compatibility up

prod_logs:
	@$(DOCKER_COMPOSE) --compatibility logs -f

prod_stop:
	@$(DOCKER_COMPOSE) --compatibility stop

prod_ps:
	@$(DOCKER_COMPOSE) --compatibility ps

prod_rm:
	@$(DOCKER_COMPOSE) --compatibility rm -f

prod_down:
	@$(DOCKER_COMPOSE) --compatibility down

prod_list_images:
	@docker images $(IMAGE_NAME}

prod_rollback:
	@echo '*** ROLLBACK TO VERSION $(APP_VERSION) ***'
	@$(DOCKER_COMPOSE) --compatibility stop
	@$(DOCKER_COMPOSE) --compatibility up -d

prod_exec_shell:
	@$(DOCKER_COMPOSE) --compatibility exec fi_admin sh

prod_exec_collectstatic:
	@$(DOCKER_COMPOSE) --compatibility exec -T fi_admin python manage.py collectstatic --noinput

prod_loaddata:
	@$(DOCKER_COMPOSE) --compatibility exec -T fi_admin python manage.py loaddata $(import_file)

prod_exec_webserver:
	@$(DOCKER_COMPOSE) --compatibility exec webserver sh

prod_make_test:
	@$(DOCKER_COMPOSE) --compatibility exec -T fi_admin make test

# import data to fi-admin
import:
	@$(DOCKER_COMPOSE) --compatibility exec -T fi_admin sh -c "cd /app/proc/import && sh import2FIAdmin.sh"

# import data to fi-admin using prod-db.env
import2prod:
	@$(DOCKER_COMPOSE) --compatibility exec -T fi_admin sh -c "set -a && . /app/proc/import/prod-db.env && set +a && cd /app/proc/import && sh import2FIAdmin.sh"
