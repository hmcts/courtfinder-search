.PHONY : test-unit test-cucumber test test-psql dev dev-psql stop

test-unit:
	docker-compose -p test build test-unit
	docker-compose -p test run test-unit

test-cucumber:
	docker-compose -p test build test-cucumber
	docker-compose -p test run test-cucumber

test: test-unit test-cucumber

test-psql:
	docker exec -ti -u postgres test_postgres_1 psql courtfinder_search

dev:
	docker-compose -p dev build courtfinder
	docker-compose -p dev run -p $${PORT:-8000}:8000 courtfinder

dev-psql:
	docker exec -ti -u postgres dev_postgres_1 psql courtfinder_search

stop:
	docker-compose -p dev stop
	docker-compose -p test stop

rm:
	docker-compose -p dev rm
	docker-compose -p test rm
