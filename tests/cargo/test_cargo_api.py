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


async def test_get_cargos(cli):
    resp = await cli.get('/spawner/cargos')
    assert resp.status == 200
    data = await resp.json()
    assert isinstance(data['cargos'], list)


async def test_post_cargos_error(cli):
    resp = await cli.post('/spawner/cargos', json={})
    assert resp.status == 400
    data = await resp.json()
    assert data["message"]


async def test_post_cargos(cli):
    body = {
        'description': "This is a test",
        'size': 10,
    }
    resp = await cli.post('/spawner/cargos', json=body)
    assert resp.status == 200
    data = await resp.json()
    assert data["message"]
