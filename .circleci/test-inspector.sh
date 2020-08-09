#!/usr/bin/env bash
set -e

docker-compose down
docker-compose up --build --remove-orphans -d

SLEEP=$2
SLEEP=${SLEEP:=10}

echo "Sleeping for $SLEEP seconds..."
sleep $SLEEP

if [ $1 == "oracle" ]
then
    echo "Seeding Oracle database..."
    docker exec -it oracle_oracle-12c_1 bash -c "source /home/oracle/.bashrc; sqlplus sys/bbk4k77JKH88g54 as sysdba @init.sql"
fi

docker-compose run --rm metamapper python manage.py test --tag="$1"
docker-compose down
