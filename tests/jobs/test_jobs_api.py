from types import MappingProxyType
from unittest.mock import patch


def _validate_token(*args):
    """Trick the _validate token to return 1."""
    payload = {
        "user_id": 1,
        "token": "fake_token"
    }
    return MappingProxyType(payload)


async def _get_limits(token: str):
    data = {
        "probes": 2,
        "cargos": 2,
        "apis": 2,
        "jobs": 2,
        "blueprints": 2,
    }
    return data

patch('utils.auth._validate_token', _validate_token).start()
patch('utils.quota._get_limits', _get_limits).start()


async def test_get_jobs(cli):
    resp = await cli.get('/spawner/jobs')
    assert resp.status == 200
    data = await resp.json()
    assert data['jobs'] == []


async def test_post_jobs_error(cli):
    resp = await cli.post('/spawner/jobs', json={})
    assert resp.status == 400
    data = await resp.json()
    assert data["error"]


async def test_post_jobs(cli):
    body = {
        'blueprint_id': 1,
        'description': "This is a test",
        'machine_type': "mega",
        'command': "python -c 'print (1)'"
    }
    resp = await cli.post('/spawner/jobs', json=body)
    assert resp.status == 200
    data = await resp.json()
    assert data["message"]
