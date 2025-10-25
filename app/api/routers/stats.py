from __future__ import annotations
from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import (
    DATEDAU,
    TopEvent,
    RetentionResponse,
    RetentionWindow
)
from app.db.session import AsyncSessionLocal
from app.services.stats_dao import get_dau, get_top_events, get_retention

router = APIRouter(prefix="/stats", tags=["stats"])


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


@router.get("/dau", response_model=List[DATEDAU])
async def stats_dau(
    from_: date = Query(..., alias="from", description="YYYY-MM-DD inclusive"),
    to:   date = Query(..., description="YYYY-MM-DD inclusive"),
    db: AsyncSession = Depends(get_db),
):
    if to < from_:
        raise HTTPException(status_code=422, detail="'to' must be >= 'from'")
    rows = await get_dau(db, from_, to)
    return [{"date": d, "unique_users": n} for d, n in rows]


@router.get("/top-events", response_model=List[TopEvent])
async def stats_top_events(
    from_: str = Query(..., alias="from", description="YYYY-MM-DD inclusive"),
    to:   str = Query(..., description="YYYY-MM-DD inclusive"),
    limit: int = Query(
        10,
        ge=1,
        le=100,
        description="Max number of event types"
    ),
    db: AsyncSession = Depends(get_db),
):

    from datetime import date
    try:
        d_from = date.fromisoformat(from_)
        d_to = date.fromisoformat(to)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="Invalid date format. Use YYYY-MM-DD"
        )

    if d_to < d_from:
        raise HTTPException(status_code=422, detail="'to' must be >= 'from'")

    rows = await get_top_events(db, d_from, d_to, limit)
    return [{"event_type": et, "count": c} for et, c in rows]


@router.get("/retention", response_model=RetentionResponse)
async def stats_retention(
    start_date: date = Query(
        ...,
        description="YYYY-MM-DD; cohort = users with first event on this date"
    ),
    windows: int = Query(
        3,
        ge=0,
        le=60,
        description="Number of daily windows (D0..D{windows})"
    ),
    db: AsyncSession = Depends(get_db),
):
    cohort_size, points = await get_retention(db, start_date, windows)

    windows_resp: List[RetentionWindow] = []
    for day, cnt in points:
        rate = (cnt / cohort_size) if cohort_size > 0 else 0.0
        windows_resp.append(RetentionWindow(
            day=day,
            count=cnt,
            rate=round(rate, 4)
        ))
    return RetentionResponse(cohort_size=cohort_size, windows=windows_resp)
