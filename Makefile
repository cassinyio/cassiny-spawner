# Some simple testing tasks (sorry, UNIX only).

SERVICE=service-spawner
POSTGRES_PASSWORD=mysecretpassword
POSTGRES_USER=postgres
POSTGRES_DB=cassiny

lint:
	@tox -e isort,flake8,mypy

clean:
	@find . -name \*.pyc -delete

run-streams:
	@docker run -d --name streams -p 4222:4222 nats-streaming:0.6.0

test:
	@docker network create test
	@docker pull minio/minio:RELEASE.2017-08-05T00-00-53Z
	@docker pull cassinyio/notebook:4018e4ee
	@docker run -d --name streams --network test -p 4222:4222 nats-streaming:0.6.0
	@docker run -d --name postgres --network test -e POSTGRES_DB=$(POSTGRES_DB) -e POSTGRES_USER=$(POSTGRES_USER) -e POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) postgres:10.0
	@docker build -t $(SERVICE) -f Dockerfile.test .
	@docker run --rm --network test -v /var/run/docker.sock:/var/run/docker.sock -e DB_HOST=postgres -e DB_USER=$(POSTGRES_USER) -e DB_PASSWORD=$(POSTGRES_PASSWORD) -e STREAM_URI=nats://streams:4222 $(SERVICE)

clean-docker:
	@docker rm -f streams
	@docker rm -f postgres
	@docker network rm test

build:
	@docker build -t $(SERVICE) -f Dockerfile .

.PHONY: lint test clean-docker build