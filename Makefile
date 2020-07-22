IMAGE_NAME=bireme/fi-admin
APP_VERSION=$(shell git describe --tags --long --always | sed 's/-g[a-z0-9]\{7\}//')
TAG_LATEST=$(IMAGE_NAME):latest

COMPOSE_FILE_DEV=docker-compose-dev.yml
COMPOSE_FILE_API=docker-compose-api.yml

## variable used in docker-compose for tag the build image
export IMAGE_TAG=$(IMAGE_NAME):$(APP_VERSION)

tag:
	@echo "IMAGE TAG:" $(IMAGE_TAG)

## docker-compose desenvolvimento
dev_build:
	@docker-compose -f $(COMPOSE_FILE_DEV) build

dev_up:
	@docker-compose -f $(COMPOSE_FILE_DEV) up -d

dev_run:
	@docker-compose -f $(COMPOSE_FILE_DEV) up

dev_logs:
	@docker-compose -f $(COMPOSE_FILE_DEV) logs -f

dev_stop:
	@docker-compose -f $(COMPOSE_FILE_DEV) stop

dev_ps:
	@docker-compose -f $(COMPOSE_FILE_DEV) ps

dev_rm:
	@docker-compose -f $(COMPOSE_FILE_DEV) rm -f

dev_exec_shell:
	@docker-compose -f $(COMPOSE_FILE_DEV) exec app sh

dev_make_test:
	@docker-compose -f $(COMPOSE_FILE_DEV) exec app make test


## docker-compose API
api_build:
	@docker-compose -f $(COMPOSE_FILE_API) --compatibility build
	@docker tag $(IMAGE_TAG) $(TAG_LATEST)

api_up:
	@docker-compose -f $(COMPOSE_FILE_API) --compatibility up -d

api_logs:
	@docker-compose -f $(COMPOSE_FILE_API) --compatibility logs -f

api_stop:
	@docker-compose -f $(COMPOSE_FILE_API) --compatibility stop

api_ps:
	@docker-compose -f $(COMPOSE_FILE_API) --compatibility ps

api_rm:
	@docker-compose -f $(COMPOSE_FILE_API) --compatibility rm -f

api_exec_shell:
	@docker-compose -f $(COMPOSE_FILE_API) --compatibility exec app sh

api_exec_collectstatic:
	@docker-compose -f $(COMPOSE_FILE_API) --compatibility exec app python manage.py collectstatic --noinput

api_exec_webserver:
	@docker-compose -f $(COMPOSE_FILE_API) --compatibility exec webserver sh

api_make_test:
	@docker-compose -f $(COMPOSE_FILE_API) --compatibility exec app make test
