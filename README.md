# Service

Collections of services offered to users

* APIs
* Probes
* Cargos
* Jobs


## Test
docker run -it --rm  --hostname my-rabbit --name some-rabbit -p 5672:5672 rabbitmq:3.6.12

docker run -it --rm -p 2181:2181 -p 9092:9092 --env ADVERTISED_HOST=127.0.0.1 --env ADVERTISED_PORT=9092 aiolibs/kafka:2.11_0.10.1.0
