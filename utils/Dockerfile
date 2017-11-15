# Copyright (c) 2017, Cassiny.io OÜ
# Distributed under the terms of the Modified BSD License.

# This is the cassinyio/base image
# used as a base for all images

# https://hub.docker.com/_/ubuntu/

FROM {{ image }}

RUN pip --quiet install falcon gunicorn ujson

WORKDIR $HOME/src

COPY . .

# need to get back to root to change permissions
USER root
RUN chown -R $NB_USER $HOME/src
USER $NB_USER

RUN pip install --quiet -r requirements.txt

EXPOSE 8080

CMD ["gunicorn", "-b :8080", "app:api", "--access-logfile=-"]
