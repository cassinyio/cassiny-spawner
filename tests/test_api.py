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
        resp = await cli.get('/spawner/apis')
        assert resp.status == 200
        data = await resp.json()
        assert data['apis'] == []

    async def test_post_apis_error(self, cli):
        resp = await cli.post('/spawner/apis', json={})
        assert resp.status == 400
        data = await resp.json()
        assert data["message"]

    async def test_post_apis(self, cli):
        body = {
            'blueprint_id': 1,
            'description': "This is a test",
            'machine_type': 1,
            'cargo_id': 1,
        }
        resp = await cli.post('/spawner/apis', json=body)
        assert resp.status == 200
        data = await resp.json()
        assert data["message"]


class TestProbes:
    async def test_get_probes(self, cli):
        resp = await cli.get('/spawner/probes')
        assert resp.status == 200
        data = await resp.json()
        assert data['probes'] == []

    async def test_post_probes_error(self, cli):
        resp = await cli.post('/spawner/probes', json={})
        assert resp.status == 400
        data = await resp.json()
        assert data["message"]

    async def test_post_probes(self, cli):
        body = {
            'blueprint_id': 1,
            'description': "This is a test",
            'machine_type': 1,
            'cargo_id': 1,
        }
        resp = await cli.post('/spawner/probes', json=body)
        assert resp.status == 200
        data = await resp.json()
        assert data["message"]


class TestBlueprints:
    async def test_get_blueprints(self, cli):
        resp = await cli.get('/spawner/blueprints')
        assert resp.status == 200
        data = await resp.json()
        assert data['blueprints'] == []


class TestJobs:
    async def test_get_jobs(self, cli):
        resp = await cli.get('/spawner/jobs')
        assert resp.status == 200
        data = await resp.json()
        assert data['jobs'] == []

    async def test_post_jobs_error(self, cli):
        resp = await cli.post('/spawner/jobs', json={})
        assert resp.status == 400
        data = await resp.json()
        assert data["message"]

    async def test_post_jobs(self, cli):
        body = {
            'blueprint_id': 1,
            'description': "This is a test",
            'machine_type': 1,
            'cargo_id': 1,
        }
        resp = await cli.post('/spawner/apis', json=body)
        assert resp.status == 200
        data = await resp.json()
        assert data["message"]


class TestCargos:
    async def test_get_cargos(self, cli):
        resp = await cli.get('/spawner/cargos')
        assert resp.status == 200
        data = await resp.json()
        assert data['cargos'] == []

    async def test_post_cargos_error(self, cli):
        resp = await cli.post('/spawner/cargos', json={})
        assert resp.status == 400
        data = await resp.json()
        assert data["message"]

    async def test_post_cargos(self, cli):
        body = {
            'blueprint_id': 1,
            'description': "This is a test",
            'machine_type': 1,
            'cargo_id': 1,
        }
        resp = await cli.post('/spawner/apis', json=body)
        assert resp.status == 200
        data = await resp.json()
        assert data["message"]
