import uuid
import pytest
from datetime import datetime, timezone
import httpx
from app.api.main import app


def zdt(y, M, d, h, m):
    return datetime(y, M, d, h, m, tzinfo=timezone.utc).isoformat()


@pytest.mark.asyncio
async def test_ingest_then_dau():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
            transport=transport,
            base_url="http://test"
    ) as client:
        payload = [
            {
                "event_id": str(uuid.uuid4()),
                "occurred_at": zdt(2025,10,20,9,0),
                "user_id": "u1",
                "event_type": "login",
                "properties": {"country":"UA"},
            },
            {
                "event_id": str(uuid.uuid4()),
                "occurred_at": zdt(2025,10,20,10,0),
                "user_id": "u2",
                "event_type": "purchase",
                "properties": {"amount": 9.99},
            },
        ]
        r = await client.post("/events", json=payload)
        assert r.status_code == 202, r.text
        assert r.json()["accepted"] == 2

        r2 = await client.get(
            "/stats/dau",
            params={"from":"2025-10-20","to":"2025-10-20"}
        )
        assert r2.status_code == 200, r2.text
        assert r2.json() == [{"date":"2025-10-20","unique_users":2}]
