# Some simple testing tasks (sorry, UNIX only).

SERVICE=service-spawner
POSTGRES_PASSWORD=mysecretpassword
POSTGRES_USER=postgres
POSTGRES_DB=cassiny

lint:
	@isort -rc -c --diff -m 3 app.py config.py factory.py create_db.py apis blueprints cargos events jobs probes spawner utils tests
	flake8 app.py config.py factory.py create_db.py apis blueprints cargos events jobs probes spawner utils tests
	@mypy app.py config.py factory.py create_db.py apis blueprints cargos events jobs probes spawner utils tests --ignore-missing-imports

test:
	@py.test --cov apis --cov blueprints --cov cargos --cov events --cov jobs --cov probes --cov spawner --cov utils --cov tests

clean:
	@find . -name \*.pyc -delete

run-services:
	@docker run -d --name streams -p 4222:4222 nats-streaming:0.7.0
	@docker run -d --name postgres -p 5432:5432 -e POSTGRES_DB=$(POSTGRES_DB) -e POSTGRES_USER=$(POSTGRES_USER) -e POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) postgres:10.0

rm-services:
	@docker rm -f streams
	@docker rm -f postgres

docker-test:
	@docker network create test
	@docker pull minio/minio:RELEASE.2017-11-22T19-55-46Z
	@docker pull cassinyio/notebook:02946e48
	@docker swarm init
	@docker run -d --name streams --network test -p 4222:4222 nats-streaming:0.7.0
	@docker run -d --name postgres --network test -e POSTGRES_DB=$(POSTGRES_DB) -e POSTGRES_USER=$(POSTGRES_USER) -e POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) postgres:10.0
	@docker build -t $(SERVICE) -f Dockerfile.test .
	@docker run --rm --network test $(SERVICE) make lint
	@docker run --rm --network test -v /var/run/docker.sock:/var/run/docker.sock -e DB_HOST=postgres -e DB_USER=$(POSTGRES_USER) -e DB_PASSWORD=$(POSTGRES_PASSWORD) -e STREAM_URI=nats://streams:4222 $(SERVICE) make test

clean-test:
	@docker rm -f streams
	@docker rm -f postgres
	@docker network rm test
	@docker swarm leave -f
