ARG POSTGRES_VERSION

FROM postgres:${POSTGRES_VERSION}

COPY postgres.sql /docker-entrypoint-initdb.d/
