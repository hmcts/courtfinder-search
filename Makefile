.PHONY : test-unit test-cucumber test test-psql dev dev-psql stop

define container-id-for
	$(shell docker ps -f 'label=com.docker.compose.project=$(1)' -f 'label=com.docker.compose.service=$(2)' -q)
endef

test: test-unit test-cucumber ## Run all tests

test-unit: ## Run unit tests
	docker-compose -p test build test-unit
	docker-compose -p test run test-unit

test-cucumber: ## Run cucumber tests
	docker-compose -p test build test-cucumber
	docker-compose -p test run test-cucumber

test-psql: ## Run psql against the test database
	docker exec -ti -u postgres $(call container-id-for,test,postgres) psql courtfinder_search

dev: ## Run the courtfinder frontend app
	docker-compose -p dev build courtfinder
	docker-compose -p dev run -p $${PORT:-8000}:8000 courtfinder

dev-psql: ## Run psql against the dev database
	docker exec -ti -u postgres $(call container-id-for,dev,postgres) psql courtfinder_search

dev-exec: ## Output the start of a docker exec against the app container
	@echo docker exec -ti $(call container-id-for,dev,courtfinder)

stop: ## Stop all dev and test containers
	docker-compose -p dev stop
	docker-compose -p test stop

rm: ## Remove all dev and test containers
	docker-compose -p dev rm
	docker-compose -p test rm
