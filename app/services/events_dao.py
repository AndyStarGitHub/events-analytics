from __future__ import annotations
from typing import Iterable, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert
from app.models.event import Event
from app.api.schemas import EventIn


async def insert_events_idempotent(
    session: AsyncSession,
    events: Iterable[EventIn],
) -> Tuple[int, int]:

    payload = [
        {
            "event_id": e.event_id,
            "occurred_at": e.occurred_at,
            "user_id": e.user_id,
            "event_type": e.event_type,
            "properties": e.properties or {},
        }
        for e in events
    ]
    if not payload:
        return (0, 0)

    stmt = pg_insert(Event).values(payload).on_conflict_do_nothing(
        index_elements=["event_id"]
    )
    result = await session.execute(stmt)

    accepted = result.rowcount if result.rowcount is not None else 0
    skipped = len(payload) - accepted
    from app.observability.metrics import EVENTS_ACCEPTED, EVENTS_SKIPPED

    EVENTS_ACCEPTED.inc(accepted)

    EVENTS_SKIPPED.inc(skipped)

    return accepted, skipped
