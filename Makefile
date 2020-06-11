CURRENT_DIRECTORY := $(shell pwd)

help:
	@echo "Metamapper"
	@echo "-----------------------"
	@echo ""
	@echo "Just starting out? Setup your development environment:"
	@echo "    make setup"
	@echo ""
	@echo "Run tests to ensure current state is good:"
	@echo "    make test"
	@echo ""
	@echo "You can also run just the Python tests:"
	@echo "    make test-py"
	@echo ""
	@echo "See contents of Makefile for more targets."

setup: build install-npm-pkgs start migrate

install-npm-pkgs:
	@npm install --prefix www

build-assets:
	@npm run build --prefix www

build-docker:
	@docker build --build-arg env=development -t metamapper --rm ./

migrate:
	@docker-compose run --rm server python manage.py migrate

reset-db: start
	@docker-compose run --rm server bash www/cypress/cmd/resetdb.sh

rebuild-db: stop
	@docker-compose start database
	@docker exec metamapper_database_1 dropdb metamapper -U postgres
	@docker exec metamapper_database_1 createdb metamapper -U postgres
	@docker-compose run -e DB_RESET=1 --rm server python manage.py migrate

start:
	@rm -f celerybeat.pid
	@docker-compose up -d --remove-orphans

stop:
	@docker-compose stop

status:
	@docker-compose ps

restart: stop start

frontend:
	@npm run start --prefix www

shell:
	@docker-compose run --rm server python manage.py shell

cypress: start
	@npx cypress open

test-ci: test-py test-js test-cypress

test-py:
	@echo "--> Running Python (server) tests"
	@find . -name \*.pyc -delete
	@docker-compose --log-level ERROR run --rm server python manage.py test

test-js:
	@echo "--> Running JavaScript (client) tests"
	@npm run test --prefix www -- --coverage

test-cypress: start
	@echo "--> Opening Cypress.io (integration tests)"
	@npx cypress run --spec "www/cypress/integration/*.spec.js"

lint: lint-py lint-js

lint-py:
	@echo "--> Linting Python"
	@bash bin/flake8-linter

lint-js:
	@echo "--> Linting JavaScript"
	@npm run lint --prefix www

.PHONY: frontend
