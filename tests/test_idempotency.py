import uuid
from datetime import datetime, timezone
from app.api.schemas import EventIn
from app.services.events_dao import insert_events_idempotent
from sqlalchemy.ext.asyncio import AsyncSession


def _ts(h=10, m=0):
    return datetime(2025, 10, 20, h, m, tzinfo=timezone.utc)


@pytest.mark.asyncio
async def test_insert_idempotent_basic(db: AsyncSession):
    e1 = EventIn(
        event_id=uuid.uuid4(),
        occurred_at=_ts(10,0),
        user_id="u1",
        event_type="login",
        properties={}
    )
    e2 = EventIn(
        event_id=uuid.uuid4(),
        occurred_at=_ts(10,5),
        user_id="u2",
        event_type="purchase",
        properties={}
    )

    acc, skip = await insert_events_idempotent(db, [e1, e2])
    await db.commit()
    assert (acc, skip) == (2, 0)

    acc2, skip2 = await insert_events_idempotent(db, [e1, e2])
    await db.commit()
    assert (acc2, skip2) == (0, 2)


@pytest.mark.asyncio
async def test_insert_idempotent_duplicates_in_same_batch(db: AsyncSession):
    event_id = uuid.uuid4()
    e1 = EventIn(
        event_id=event_id,
        occurred_at=_ts(11,0),
        user_id="u1",
        event_type="x",
        properties={}
    )
    e2 = EventIn(
        event_id=event_id,
        occurred_at=_ts(11,1),
        user_id="u2",
        event_type="y",
        properties={}
    )
    acc, skip = await insert_events_idempotent(db, [e1, e2])
    await db.commit()
    assert (acc, skip) == (1, 1)
