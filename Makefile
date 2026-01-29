IMAGE_NAME=bireme/fi-admin
APP_VERSION?=$(shell git describe --tags --long --always | sed 's/-g[a-z0-9]\{7\}//' | sed 's/-/\./')
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

dev_down:
	@docker-compose -f $(COMPOSE_FILE_DEV) down

dev_ps:
	@docker-compose -f $(COMPOSE_FILE_DEV) ps

dev_rm:
	@docker-compose -f $(COMPOSE_FILE_DEV) rm -f

dev_sh:
	@docker-compose -f $(COMPOSE_FILE_DEV) exec fi_admin sh

dev_makemigrations:
	@docker-compose -f $(COMPOSE_FILE_DEV) exec fi_admin python manage.py makemigrations $(app)

dev_migrate:
	@docker-compose -f $(COMPOSE_FILE_DEV) exec fi_admin python manage.py migrate $(app)

dev_test:
	@docker-compose -f $(COMPOSE_FILE_DEV) exec fi_admin make test

dev_update_translations:
	@docker-compose -f $(COMPOSE_FILE_DEV) exec fi_admin sh -c "apk add --no-cache gettext && python manage.py makemessages --all"

dev_import:
	@docker-compose -f $(COMPOSE_FILE_DEV) exec -T fi_admin python manage.py loaddata $(import_file)


## docker-compose API
api_build:
	@docker-compose -f $(COMPOSE_FILE_API) --compatibility build
	@docker tag $(IMAGE_TAG) $(TAG_LATEST)

api_up:
	@docker-compose -f $(COMPOSE_FILE_API) --compatibility up -d

api_run:
	@docker-compose -f $(COMPOSE_FILE_API) --compatibility up

api_logs:
	@docker-compose -f $(COMPOSE_FILE_API) --compatibility logs -f

api_stop:
	@docker-compose -f $(COMPOSE_FILE_API) --compatibility stop

api_ps:
	@docker-compose -f $(COMPOSE_FILE_API) --compatibility ps

api_rm:
	@docker-compose -f $(COMPOSE_FILE_API) --compatibility rm -f

api_rollback:
	@echo '*** ROLLBACK TO VERSION $(APP_VERSION) ***'
	@docker-compose -f $(COMPOSE_FILE_API) --compatibility stop
	@docker-compose -f $(COMPOSE_FILE_API) --compatibility up -d

api_exec_shell:
	@docker-compose -f $(COMPOSE_FILE_API) --compatibility exec fi_admin_api sh

api_exec_collectstatic:
	@docker-compose -f $(COMPOSE_FILE_API) --compatibility exec -T fi_admin_api python manage.py collectstatic --noinput

api_exec_webserver:
	@docker-compose -f $(COMPOSE_FILE_API) --compatibility exec webserver sh

api_make_test:
	@docker-compose -f $(COMPOSE_FILE_API) --compatibility exec -T fi_admin_api make test

## docker-compose prod
prod_build:
	@docker-compose --compatibility build
	@docker tag $(IMAGE_TAG) $(TAG_LATEST)

prod_up:
	@docker-compose --compatibility up -d

prod_run:
	@docker-compose --compatibility up

prod_logs:
	@docker-compose --compatibility logs -f

prod_stop:
	@docker-compose --compatibility stop

prod_ps:
	@docker-compose --compatibility ps

prod_rm:
	@docker-compose --compatibility rm -f

prod_list_images:
	@docker images $(IMAGE_NAME}

prod_rollback:
	@echo '*** ROLLBACK TO VERSION $(APP_VERSION) ***'
	@docker-compose --compatibility stop
	@docker-compose --compatibility up -d

prod_exec_shell:
	@docker-compose --compatibility exec fi_admin sh

prod_exec_collectstatic:
	@docker-compose --compatibility exec -T fi_admin python manage.py collectstatic --noinput

prod_import:
	@docker-compose --compatibility exec -T fi_admin python manage.py loaddata $(import_file)

prod_exec_webserver:
	@docker-compose --compatibility exec webserver sh

prod_make_test:
	@docker-compose --compatibility exec -T fi_admin make test
