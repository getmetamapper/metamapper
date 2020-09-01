ARG MYSQL_VERSION

FROM mysql:${MYSQL_VERSION}

COPY mysql.sql /docker-entrypoint-initdb.d/
