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

test-security-cucumber: ## Run cucumber through ZAP
	docker-compose -p test build test-security
	docker-compose -p test run test-security
	# Get the HTML report
	docker exec $(call container-id-for,test,zap) zap-cli -p 8089 report -f html -o /tmp/test-security-cucumber-result.html
	# Show the result
	docker cp $(call container-id-for,test,zap):/tmp/test-security-cucumber-result.html .
	@echo "Open test-security-cucumber-result.html in your browser"

test-security-scan: ## Run a ZAP crawl based scan
	docker-compose -p test run test-security
	# Run the scan
	docker exec $(call container-id-for,test,zap) zap-cli -p 8089 quick-scan --spider --recursive --alert-level Medium --start-options '-config api.disablekey=true' http://courtfinder:8000
	# Get the HTML report
	docker exec $(call container-id-for,test,zap) zap-cli -p 8089 report -f html -p /tmp/test-security-scan-result.html
	# Reset so subsequent runs do not have these results in
	docker exec $(call container-id-for,test,zap) zap-cli -p 8089 session new
	# Show the result
	docker cp $(call container-id-for,test,zap):/tmp/test-security-scan-result.html .
	@echo "Open test-security-scan-result.html in your browser"

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
