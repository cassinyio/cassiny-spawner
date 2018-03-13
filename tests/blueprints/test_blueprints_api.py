async def test_get_blueprints(cli, valid_token):
    resp = await cli.get('/api/spawner/blueprints')
    assert resp.status == 200
    data = await resp.json()
    assert data['blueprints']
