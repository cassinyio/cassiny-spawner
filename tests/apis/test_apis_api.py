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


class TestAPIS:
    async def test_get_apis(self, cli):
        resp = await cli.get('/api/spawner/apis')
        assert resp.status == 200
        data = await resp.json()
        assert data['apis'] == []

    async def test_post_apis_error(self, cli):
        resp = await cli.post('/api/spawner/apis', json={})
        assert resp.status == 400
        data = await resp.json()
        assert data["error"]

    async def test_post_apis(self, cli):
        body = {
            'blueprint': "2a83d4be0f7011e89e4b35694e577c22",
            'description': "This is a test",
            'machine_type': "mega",
            'command': "python app.py 0.0.0.0:8080",
            'preemptible': False,
            'gpu': False
        }
        resp = await cli.post('/api/spawner/apis', json=body)
        assert resp.status == 200
        data = await resp.json()
        assert data["message"]
