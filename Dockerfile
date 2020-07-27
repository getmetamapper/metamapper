FROM node:12 as frontend-builder

ARG env

ENV NODE_ENV $env

WORKDIR /frontend
COPY /www /frontend

RUN npm ci --unsafe-perm
RUN npm run build

FROM python:3.7-stretch as base

ENV PYTHONUNBUFFERED 1
ENV LD_LIBRARY_PATH /opt/oracle
ENV BASE_DIR /usr/local/metamapper/

RUN groupadd -r metamapper && useradd -r -m -g metamapper metamapper

# Ubuntu packages
RUN apt-get update -y && apt-get install -y \
    libxml2-dev \
    libxmlsec1-dev \
    libxmlsec1-openssl \
    g++ \
    unixodbc-dev \
    libaio1

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

ADD ./Pipfile $BASE_DIR
ADD ./Pipfile.lock $BASE_DIR

RUN pip install --upgrade pip
RUN pip install 'pipenv==2018.11.26' --quiet
RUN pipenv install --dev --system

ADD . $BASE_DIR
COPY --from=frontend-builder /frontend/build ${BASE_DIR}/www/build

RUN chmod +x ${BASE_DIR}bin/docker-entrypoint

ENTRYPOINT ["./bin/docker-entrypoint"]
