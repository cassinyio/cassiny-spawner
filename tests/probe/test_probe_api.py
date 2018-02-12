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


async def test_get_probes(cli):
    resp = await cli.get('/spawner/probes')
    assert resp.status == 200
    data = await resp.json()
    assert isinstance(data['probes'], list)


async def test_post_probes_error(cli):
    resp = await cli.post('/spawner/probes', json={})
    assert resp.status == 400
    data = await resp.json()
    assert data["error"]


async def test_post_probes(cli):
    body = {
        'blueprint': "2a83d4be-0f70-11e8-9e4b-35694e577c22",
        'description': "This is a test",
        'machine_type': "mega",
        'preemptible': True,
        'gpu': True
    }
    resp = await cli.post('/spawner/probes', json=body)
    assert resp.status == 200
    data = await resp.json()
    assert data["message"]
