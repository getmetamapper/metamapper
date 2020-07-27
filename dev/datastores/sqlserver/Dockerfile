ARG MSSQL_IMAGE
ARG MSSQL_VERSION

FROM ${MSSQL_IMAGE}:${MSSQL_VERSION}

USER root

ENV SA_PASSWORD=6095A5f58910e18a4c8
ENV SQLCMDPASSWORD=6095A5f58910e18a4c8

# Create app directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY . /usr/src/app

# Grant permissions for the import-data script to be executable
RUN chmod +x /usr/src/app/init.sh

ENTRYPOINT /bin/bash ./entrypoint.sh
