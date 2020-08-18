CURRENT_DIRECTORY := $(shell pwd)

help:
	@echo ""
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
	@echo ""

setup: install-npm-pkgs build-assets build-docker initdb

install-npm-pkgs:
	@npm install --prefix www --quiet

build-assets:
	@npm run build --prefix www

build-docker:
	@docker build --build-arg env=development -t metamapper --rm ./

initdb:
	@docker-compose run -e DB_SETUP=1 --rm webserver python manage.py initdb --noinput --verbosity 0

migrate:
	@docker-compose run -e DB_SETUP=1 --rm webserver python manage.py migrate

resetdb:
	@docker-compose run --rm webserver bash www/cypress/cmd/resetdb.sh

rebuild-db: stop
	@docker-compose start database
	@docker exec metamapper_database_1 dropdb metamapper -U postgres
	@docker exec metamapper_database_1 createdb metamapper -U postgres
	@docker-compose run -e DB_RESET=1 --rm webserver python manage.py migrate

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
	@docker-compose run --rm webserver python manage.py shell

cypress-resetdb:
	@docker-compose run --rm webserver bash www/cypress/cmd/resetdb.sh

cypress: cypress-resetdb
	@npx cypress open

test-cypress: cypress-resetdb
	@echo "--> Running Cypress (integration) tests"
	@npx cypress run --spec "www/cypress/integration/*.spec.js" --browser chrome --headless

test-py:
	@echo "--> Running Python (webserver) tests"
	@find . -name \*.pyc -delete
	@docker-compose --log-level ERROR run --rm webserver python manage.py test --exclude-tag=inspector

test-js:
	@echo "--> Running JavaScript (client) tests"
	@npm run test --prefix www

lint: lint-py lint-js

lint-py:
	@echo "--> Linting Python"
	@bash bin/flake8-linter

lint-js:
	@echo "--> Linting JavaScript"
	@npm run lint --prefix www

.PHONY: frontend
