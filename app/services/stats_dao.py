from __future__ import annotations
from datetime import date, datetime, timedelta
from typing import List, Tuple

from sqlalchemy import select, func, cast, Date, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event


async def get_dau(
    session: AsyncSession,
    date_from: date,
    date_to: date,
) -> List[Tuple[date, int]]:

    start_ts = datetime.combine(date_from, datetime.min.time())
    end_ts   = datetime.combine(
        date_to,
        datetime.min.time()
    ) + timedelta(days=1)

    day_col = cast(Event.occurred_at, Date)
    stmt = (
        select(
            day_col.label("day"),
            func.count(func.distinct(Event.user_id)).label("unique_users")
        )
        .where(Event.occurred_at >= start_ts, Event.occurred_at < end_ts)
        .group_by(day_col)
        .order_by(day_col)
    )
    rows = (await session.execute(stmt)).all()
    return [(r.day, r.unique_users) for r in rows]


async def get_top_events(
    session: AsyncSession,
    date_from: date,
    date_to: date,
    limit: int = 10,
) -> List[Tuple[str, int]]:

    start_ts = datetime.combine(date_from, datetime.min.time())
    end_ts = datetime.combine(
        date_to,
        datetime.min.time()
    ) + timedelta(days=1)

    stmt = (
        select(Event.event_type, func.count().label("cnt"))
        .where(Event.occurred_at >= start_ts, Event.occurred_at < end_ts)
        .group_by(Event.event_type)
        .order_by(func.count().desc())
        .limit(limit)
    )
    rows = (await session.execute(stmt)).all()
    return [(r.event_type, r.cnt) for r in rows]


async def get_retention(
    session: AsyncSession,
    start_date: date,
    windows: int,
) -> Tuple[int, List[Tuple[int, int]]]:

    cohort_sql = text("""
        WITH first_events AS (
            SELECT user_id, MIN(occurred_at::date) AS first_date
            FROM events
            GROUP BY user_id
        )
        SELECT COUNT(*) AS cohort_size
        FROM first_events
        WHERE first_date = :start_date
    """)
    cohort_size = (await session.execute(
        cohort_sql,
        {"start_date": start_date}
    )).scalar_one()

    if cohort_size == 0:
        return 0, [(d, 0) for d in range(0, windows + 1)]

    windows_sql = text("""
        WITH cohort AS (
            SELECT user_id
            FROM (
                SELECT user_id, MIN(occurred_at::date) AS first_date
                FROM events
                GROUP BY user_id
            ) t
            WHERE t.first_date = :start_date
        ),
        days AS (
            SELECT generate_series(0, :windows) AS d
        )
        SELECT
            d AS day,
            COUNT(DISTINCT e.user_id) AS cnt
        FROM days
        LEFT JOIN events e
          ON e.user_id IN (SELECT user_id FROM cohort)
         AND e.occurred_at >= (CAST(:start_date AS date) + (d * INTERVAL '1 day'))
         AND e.occurred_at <  (CAST(:start_date AS date) + ((d + 1) * INTERVAL '1 day'))
        GROUP BY d
        ORDER BY d
    """)

    rows = (await session.execute(
        windows_sql,
        {"start_date": start_date, "windows": windows}
    )).all()

    return cohort_size, [(r.day, r.cnt) for r in rows]
