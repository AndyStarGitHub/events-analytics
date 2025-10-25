from __future__ import annotations

from starlette.requests import Request

from app.core.metrics import EVENTS_INGESTED, INGEST_DURATION, Timer
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.schemas import EventsBatchIn, IngestResult
from app.core.config import get_settings
from app.db.session import AsyncSessionLocal
from app.services.events_dao import insert_events_idempotent


router = APIRouter(prefix="/events", tags=["events"])


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


@router.post(
    "",
    response_model=IngestResult,
    status_code=status.HTTP_202_ACCEPTED
)
async def ingest_events(
    batch: EventsBatchIn,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    settings = get_settings()

    if len(batch) == 0:
        raise HTTPException(status_code=422, detail="Empty batch")
    if len(batch) > settings.MAX_BATCH_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Batch too large. MAX_BATCH_SIZE={settings.MAX_BATCH_SIZE}",
        )

    with Timer(INGEST_DURATION):
        accepted, skipped = await insert_events_idempotent(db, batch)
        await db.commit()

    if accepted:
        EVENTS_INGESTED.labels("accepted").inc(accepted)
    if skipped:
        EVENTS_INGESTED.labels("skipped").inc(skipped)

    return IngestResult(accepted=accepted, skipped=skipped)
