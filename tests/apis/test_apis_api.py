async def test_get_apis(cli, valid_token):
    resp = await cli.get('/api/spawner/apis')
    assert resp.status == 200
    data = await resp.json()
    assert data['apis'] == []


async def test_post_apis_error(cli, valid_token):
    resp = await cli.post('/api/spawner/apis', json={})
    assert resp.status == 400
    data = await resp.json()
    assert data["error"]


async def test_post_apis(cli, valid_token):
    body = {
        'blueprint': "2a83d4be0f7011e89e4b35694e577c22",
        'description': "This is a test",
        'machine_type': "medium",
        'command': "python app.py 0.0.0.0:8080",
        'gpu': False
    }
    resp = await cli.post('/api/spawner/apis', json=body)
    assert resp.status == 200
    data = await resp.json()
    assert data["message"]
