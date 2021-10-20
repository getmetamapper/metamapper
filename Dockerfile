FROM node:12 as frontend-builder

ARG env

ENV NODE_ENV $env

WORKDIR /frontend
COPY /www /frontend

RUN npm ci --unsafe-perm --loglevel silent
RUN npm run build --loglevel silent

FROM python:3.7-stretch as base

ENV PYTHONUNBUFFERED 1
ENV LD_LIBRARY_PATH /opt/oracle
ENV BASE_DIR /usr/local/metamapper/
ENV PYMSSQL_BUILD_WITH_BUNDLED_FREETDS 0

RUN groupadd -r metamapper && useradd -r -m -g metamapper metamapper

# Ubuntu packages
RUN apt-get update -y && apt-get install -y \
    libxml2-dev \
    libxmlsec1-dev \
    libxmlsec1-openssl \
    g++ \
    unixodbc-dev \
    libaio1

# MS-SQL support for SSL connections
RUN mkdir -p /opt/microsoft && \
    cd /opt/microsoft && \
    wget ftp://ftp.freetds.org/pub/freetds/stable/freetds-1.2.tar.gz && \
    tar -xzf freetds-1.2.tar.gz && \
    cd freetds-1.2 && \
    ./configure --prefix=/usr/local --with-tdsver=7.3 && \
    make && make install && \
    ln -s /usr/local/lib/libsybdb.so.5 /usr/lib/libsybdb.so.5 && \
    ldconfig

# Oracle Database support
RUN mkdir -p /opt/oracle && \
    cd /opt/oracle && \
    wget --quiet https://download.oracle.com/otn_software/linux/instantclient/19600/instantclient-basiclite-linux.x64-19.6.0.0.0dbru.zip && \
    unzip instantclient-basiclite-linux.x64-19.6.0.0.0dbru.zip && \
    rm -rf instantclient-basiclite-linux.x64-19.6.0.0.0dbru.zip && \
    sh -c "echo /opt/oracle/instantclient_19_6 > /etc/ld.so.conf.d/oracle-instantclient.conf" \
    ldconfig

ENV LD_LIBRARY_PATH /opt/oracle/instantclient_19_6:$LD_LIBRARY_PATH

RUN mkdir $BASE_DIR
WORKDIR $BASE_DIR

COPY --from=frontend-builder /frontend/build ${BASE_DIR}/www/build

ADD ./requirements.in $BASE_DIR
ADD ./requirements.txt $BASE_DIR
ADD ./requirements-dev.in $BASE_DIR
ADD ./requirements-dev.txt $BASE_DIR

RUN pip install --upgrade pip
RUN pip install pip-tools --quiet
RUN pip-sync requirements.txt requirements-dev.txt --quiet
RUN pip install --upgrade --force-reinstall --no-binary pymssql pymssql --quiet

ADD . $BASE_DIR

RUN chmod +x ${BASE_DIR}bin/docker-entrypoint

ENTRYPOINT ["./bin/docker-entrypoint"]
