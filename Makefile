# Some simple testing tasks (sorry, UNIX only).

SERVICE=service-spawner
POSTGRES_PASSWORD=mysecretpassword
POSTGRES_USER=postgres
POSTGRES_DB=cassiny

lint:
	@tox -e isort,flake8,mypy

test:
	@docker network create test
	@docker pull minio/minio:RELEASE.2017-08-05T00-00-53Z
	@docker pull cassinyio/notebook:4018e4ee
	@docker run -d --name kafka --network test -e ADVERTISED_HOST=kafka -e ADVERTISED_PORT=9092  cassinyio/kafka:2.11_1.0.0
	@docker run -d --name postgres --network test -e POSTGRES_DB=$(POSTGRES_DB) -e POSTGRES_USER=$(POSTGRES_USER) -e POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) postgres:10.0
	@docker build -t $(SERVICE) -f Dockerfile.test .
	@docker swarm init
	@docker run --rm --network test -v /var/run/docker.sock:/var/run/docker.sock -e DB_HOST=postgres -e DB_USER=$(POSTGRES_USER) -e DB_PASSWORD=$(POSTGRES_PASSWORD) -e KAFKA_URI=kafka:9092 $(SERVICE)

clean-docker:
	@docker rm -f kafka
	@docker rm -f postgres
	@docker network rm test
	@docker swarm leave -f

build:
	@docker build -t $(SERVICE) -f Dockerfile .

.PHONY: lint test clean-docker build