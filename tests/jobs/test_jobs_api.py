import asyncio


async def test_get_jobs(cli, valid_token):
    resp = await cli.get('/api/spawner/jobs')
    assert resp.status == 200
    data = await resp.json()
    assert data['jobs'] == []


async def test_post_jobs_error(cli, valid_token):
    resp = await cli.post('/api/spawner/jobs', json={})
    assert resp.status == 400
    data = await resp.json()
    assert data["error"]


async def test_post_jobs(cli, valid_token):
    body = {
        'blueprint': "2a83d4be-0f70-11e8-9e4b-35694e577c22",
        'description': "This is a test",
        'machine_type': "medium",
        'command': "python -c 'print (1)'",
        'gpu': False
    }
    resp = await cli.post('/api/spawner/jobs', json=body)
    assert resp.status == 200
    data = await resp.json()
    assert data["message"]

async def test_delete_jobs(cli, valid_token):
    body = {
        'blueprint': "2a83d4be-0f70-11e8-9e4b-35694e577c22",
        'description': "This is a test",
        'machine_type': "medium",
        'command': "python -c 'print (1)'",
        'gpu': False
    }
    resp = await cli.post('/api/spawner/jobs', json=body)
    assert resp.status == 200
    data = await resp.json()
    uuid = data['uuid']
    await asyncio.sleep(5)
    resp = await cli.delete(f'/api/spawner/jobs/{uuid}')
    assert resp.status == 200
