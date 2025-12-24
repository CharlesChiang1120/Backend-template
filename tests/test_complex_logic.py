import pytest
@pytest.mark.asyncio
async def test_admin_can_access_device_metadata(client):
    login_res = await client.post("/api/v1/login", json={"username": "admin", "password": "123"})
    token = login_res.json()["access_token"]
    res = await client.get("/api/v1/devices/1", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["name"] == "CNC-001"