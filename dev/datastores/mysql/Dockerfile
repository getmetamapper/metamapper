ARG MYSQL_VERSION

FROM mysql:${MYSQL_VERSION}

COPY init.sql /docker-entrypoint-initdb.d/
