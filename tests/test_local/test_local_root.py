def test_default(client):
    resp = client.get("/default")

    assert resp.status_code == 200
    assert resp.json()['server']['environment'] == "Development"