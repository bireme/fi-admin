COMPOSE_FILE_DEV = docker-compose-dev.yml
COMPOSE_FILE_API = docker-compose-api.yml

export APP_BUILD_DATE=$(shell date -u +"%Y-%m-%dT%H:%M:%SZ")

build_date:
	@echo "Build date: " $(APP_BUILD_DATE)

## docker-compose desenvolvimento 
dev_build:
	@docker-compose -f $(COMPOSE_FILE_DEV) build

dev_up:
	@docker-compose -f $(COMPOSE_FILE_DEV) up -d

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
	@docker-compose -f $(COMPOSE_FILE_API) build

api_up:
	@docker-compose -f $(COMPOSE_FILE_API) --compatibility up -d

api_logs:
	@docker-compose -f $(COMPOSE_FILE_API) logs -f 

api_stop:
	@docker-compose -f $(COMPOSE_FILE_API) stop

api_ps:
	@docker-compose -f $(COMPOSE_FILE_API) ps

api_rm:
	@docker-compose -f $(COMPOSE_FILE_API) rm -f

api_exec_shell:
	@docker-compose -f $(COMPOSE_FILE_API) exec app sh

api_exec_collectstatic:
	@docker-compose -f $(COMPOSE_FILE_API) exec app python manage.py collectstatic --noinput

api_exec_webserver:
	@docker-compose -f $(COMPOSE_FILE_API) exec webserver sh

api_make_test:
	@docker-compose -f $(COMPOSE_FILE_API) exec app make test
