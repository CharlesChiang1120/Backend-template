import pytest
@pytest.mark.asyncio
async def test_ai_ask_endpoint(client):
    res = await client.post("/api/v1/ai/ask?prompt=Hello")
    assert res.status_code == 200