# !/bin/sh

RESULT=1

for i in $(cat cypress.json | jq -r '.testFiles[]'); do
    echo "$i"

    docker-compose run --rm webserver bash www/cypress/cmd/resetdb.sh
    docker-compose run --rm cypress npx cypress run --spec "www/cypress/integration/$i" --headless --browser chrome; RESULT=$?

    if [[ $RESULT != 0 ]]; then
        exit 1
    fi
done
