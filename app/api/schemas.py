from datetime import date, datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator
from uuid import UUID


class EventIn(BaseModel):
    event_id: UUID
    occurred_at: datetime = Field(description="ISO-8601 timestamp")
    user_id: str
    event_type: str
    properties: Optional[Dict[str, Any]] = None

    @field_validator("user_id", "event_type")
    @classmethod
    def non_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("must be non-empty")
        return v


EventsBatchIn = List[EventIn]


class IngestResult(BaseModel):
    accepted: int
    skipped: int


class DATEDAU(BaseModel):
    date: date
    unique_users: int


class TopEvent(BaseModel):
    event_type: str
    count: int


class RetentionWindow(BaseModel):
    day: int
    count: int
    rate: float  # 0..1


class RetentionResponse(BaseModel):
    cohort_size: int
    windows: List[RetentionWindow]


DATEDAU.model_rebuild()
RetentionWindow.model_rebuild()
RetentionResponse.model_rebuild()
