# Copyright (c) 2017, Cassiny.io OÜ

FROM python:3.6.4-alpine

LABEL maintainer "wow@cassiny.io"

RUN apk update && \
    apk add build-base && \
    apk add postgresql-dev

RUN mkdir /src
WORKDIR /src
COPY requirements /src/requirements

RUN pip --no-cache-dir install -r requirements/common.txt

COPY . /src

CMD ["./run.sh"]
