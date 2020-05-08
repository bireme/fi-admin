COMPOSE_FILE_DEV = docker-compose-dev.yml
COMPOSE_FILE_API = docker-compose-api.yml

export APP_BUILD_DATE=$(shell date -u +"%Y-%m-%dT%H:%M:%SZ")

build_date:
	@echo "Build date: " $(APP_BUILD_DATE)

## docker-compose desenvolvimento 
dev_compose_build:
	@docker-compose -f $(COMPOSE_FILE_DEV) build

dev_compose_up:
	@docker-compose -f $(COMPOSE_FILE_DEV) up -d

dev_compose_logs:
	@docker-compose -f $(COMPOSE_FILE_DEV) logs -f 

dev_compose_stop:
	@docker-compose -f $(COMPOSE_FILE_DEV) stop

dev_compose_ps:
	@docker-compose -f $(COMPOSE_FILE_DEV) ps

dev_compose_rm:
	@docker-compose -f $(COMPOSE_FILE_DEV) rm -f

dev_compose_exec_shell:
	@docker-compose -f $(COMPOSE_FILE_DEV) exec app sh

dev_compose_make_test:
	@docker-compose -f $(COMPOSE_FILE_DEV) exec app make test


## docker-compose API
api_compose_build:
	@docker-compose -f $(COMPOSE_FILE_API) build

api_compose_up:
	@docker-compose -f $(COMPOSE_FILE_API) up -d

api_compose_logs:
	@docker-compose -f $(COMPOSE_FILE_API) logs -f 

api_compose_stop:
	@docker-compose -f $(COMPOSE_FILE_API) stop

api_compose_ps:
	@docker-compose -f $(COMPOSE_FILE_API) ps

api_compose_rm:
	@docker-compose -f $(COMPOSE_FILE_API) rm -f

api_compose_exec_shell:
	@docker-compose -f $(COMPOSE_FILE_API) exec app sh

api_compose_exec_collectstatic:
	@docker-compose -f $(COMPOSE_FILE_API) exec app python manage.py collectstatic --noinput

api_compose_exec_ngnix:
	@docker-compose -f $(COMPOSE_FILE_API) exec nginx sh

api_compose_make_test:
	@docker-compose -f $(COMPOSE_FILE_API) exec app make test
