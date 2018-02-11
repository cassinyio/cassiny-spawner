from secrets import token_urlsafe

from spawner import Spawner
from utils import naminator, get_uuid


async def test_create_remove_job(loop):
    name = naminator("job")
    specs = {
        "repository": "cassinyio",
        "blueprint": "notebook:4018e4ee",
        "cpu": 1,
        "ram": 100,
        "service_type": "job",
        "command": "python -c 'for i in range(100): print(i)'",
        "uuid": get_uuid().hex,
    }

    await Spawner.job.create(
        name=name,
        user_id=1,
        specs=specs,
    )
    service = await Spawner.get_service(name=name)
    assert service is not None
    await Spawner.job.delete(name=name)
    service = await Spawner.get_service(name=name)
    assert service is None


async def create_remove_api(loop):
    name = naminator("api")
    specs = {
        "repository": "cassinyio",
        "blueprint": "notebook:4018e4ee",
        "cpu": 1,
        "ram": 100,
        "service_type": "api",
        "command": "python -c 'for i in range(100): print(i)'",
        "uuid": get_uuid().hex,
    }

    await Spawner.api.create(
        name=name,
        user_id=1,
        specs=specs,
        cargo=1,
        s3_key="test",
        s3_skey="test",
    )
    service = await Spawner.get_service(name=name)
    assert service is not None
    await Spawner.api.delete(name=name)
    service = await Spawner.get_service(name=name)
    assert service is None


async def test_create_remove_probe(loop):
    name = naminator("probe")
    token = token_urlsafe(30)
    specs = {
        "repository": "cassinyio",
        "blueprint": "notebook:4018e4ee",
        "cpu": 1,
        "ram": 100,
        "service_type": "probe",
        "uuid": get_uuid().hex,
    }

    await Spawner.probe.create(
        name=name,
        user_id=1,
        specs=specs,
        token=token
    )
    service = await Spawner.get_service(name=name)
    assert service is not None
    await Spawner.probe.delete(name=name)
    service = await Spawner.get_service(name=name)
    assert service is None


async def test_create_remove_cargo(loop):
    name = naminator("cargo")
    specs = {
        "cpu": 1,
        "ram": 100,
        "service_type": "cargo",
        'args': "server /data",
        'repository': "minio",
        'blueprint': "minio:RELEASE.2017-08-05T00-00-53Z",
        "uuid": get_uuid().hex,
    }

    await Spawner.cargo.create(
        name=name,
        user_id=1,
        access_key=token_urlsafe(15).upper(),
        secret_key=token_urlsafe(30),
        specs=specs,
    )
    service = await Spawner.get_service(name=name)
    assert service is not None
    await Spawner.cargo.delete(name=name)
    service = await Spawner.get_service(name=name)
    assert service is None
