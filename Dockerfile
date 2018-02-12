# Copyright (c) 2017, Cassiny.io OÜ

FROM python:3.6.4

LABEL maintainer "wow@cassiny.io"

USER root

RUN mkdir /src
WORKDIR /src
COPY requirements /src/requirements

# Install python packages
RUN pip --no-cache-dir install -r requirements/common.txt

COPY . /src

# Configure container startup
CMD ["python", "app.py", "0.0.0.0"]