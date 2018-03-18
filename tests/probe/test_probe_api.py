async def test_get_probes(cli, valid_token):
    resp = await cli.get('/api/spawner/probes')
    assert resp.status == 200
    data = await resp.json()
    assert isinstance(data['probes'], list)


async def test_post_probes_error(cli, valid_token):
    resp = await cli.post('/api/spawner/probes', json={})
    assert resp.status == 400
    data = await resp.json()
    assert data["error"]


async def test_post_probes(cli, valid_token):
    body = {
        'blueprint': "2a83d4be-0f70-11e8-9e4b-35694e577c22",
        'description': "This is a test",
        'machine_type': "medium",
        'preemptible': True,
        'gpu': True
    }
    resp = await cli.post('/api/spawner/probes', json=body)
    assert resp.status == 200
    data = await resp.json()
    assert data["message"]
