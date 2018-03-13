async def test_get_cargos(cli, valid_token):
    resp = await cli.get('/api/spawner/cargos')
    assert resp.status == 200
    data = await resp.json()
    assert isinstance(data['cargos'], list)


async def test_post_cargos_error(cli, valid_token):
    resp = await cli.post('/api/spawner/cargos', json={})
    assert resp.status == 400
    data = await resp.json()
    assert data["message"]


async def test_post_cargos(cli, valid_token):
    body = {
        'description': "This is a test",
        'size': 10,
    }
    resp = await cli.post('/api/spawner/cargos', json=body)
    assert resp.status == 200
    data = await resp.json()
    assert data["message"]
