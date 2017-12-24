
docker_string = '''
# Copyright (c) 2017, Cassiny.io OÜ
# Distributed under the terms of the Modified BSD License.

FROM {image}

LABEL maintainer "wow@cassiny.io"

WORKDIR $HOME/src

COPY . .

# need to get back to root to change permissions
USER root
RUN chown -R $NB_USER $HOME/src
USER $NB_USER

RUN pip install --quiet -r requirements.txt

EXPOSE 8080

'''
