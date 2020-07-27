#!/usr/bin/env bash
set -e

docker-compose down
docker-compose up --build --remove-orphans -d

sleep 10

docker-compose run --rm metamapper python manage.py test --tag="$1"
docker-compose down
