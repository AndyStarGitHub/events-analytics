from __future__ import annotations
import csv
import json
import argparse
from typing import List, Dict, Any
from uuid import UUID

from datetime import datetime
import asyncio
import structlog

from app.core.config import get_settings
from app.db.session import AsyncSessionLocal
from app.api.schemas import EventIn
from app.services.events_dao import insert_events_idempotent

log = structlog.get_logger()


def _parse_dt_iso8601(value: str) -> datetime:

    v = value.strip()
    if v.endswith("Z"):
        v = v[:-1] + "+00:00"
    return datetime.fromisoformat(v)


def _parse_properties(value: str) -> Dict[str, Any]:
    if not value or value.strip() == "":
        return {}
    try:
        obj = json.loads(value)
        if isinstance(obj, dict):
            return obj

        return {"_value": obj}
    except json.JSONDecodeError:
        return {"_raw": value}


async def _process_batch(rows: List[Dict[str, str]]) -> tuple[int, int]:

    events: List[EventIn] = []
    for r in rows:
        try:
            e = EventIn(
                event_id=UUID(r["event_id"]),
                occurred_at=_parse_dt_iso8601(r["occurred_at"]),
                user_id=r["user_id"].strip(),
                event_type=r["event_type"].strip(),
                properties=_parse_properties(r.get("properties_json", "")),
            )
            events.append(e)
        except Exception as ex:
            log.warning("import_row_skipped_invalid", error=str(ex), row=r)

    if not events:
        return (0, len(rows))

    async with AsyncSessionLocal() as session:
        accepted, skipped = await insert_events_idempotent(session, events)
        await session.commit()
        return (accepted, skipped + (len(rows) - len(events)))


async def _run(path: str, batch_size: int, dry_run: bool) -> None:
    settings = get_settings()
    bs = min(batch_size, settings.MAX_BATCH_SIZE)
    total_read = total_accepted = total_skipped = 0

    log.info("import_start", path=path, batch_size=bs, dry_run=dry_run)

    if dry_run:
        log.info(
            "import_dry_run_warning",
            note="Файл буде прочитано, але в БД нічого не пишемо"
        )

    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {
            "event_id",
            "occurred_at",
            "user_id",
            "event_type",
            "properties_json"
        }
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise RuntimeError(
                f"CSV is missing required columns: {sorted(missing)}"
            )

        buf: List[Dict[str, str]] = []
        for row in reader:
            buf.append(row)
            if len(buf) >= bs:
                total_read += len(buf)
                if dry_run:
                    log.info(
                        "import_batch_dry",
                        read=len(buf),
                        total_read=total_read
                    )
                else:
                    a, s = await _process_batch(buf)
                    total_accepted += a
                    total_skipped += s
                    log.info("import_batch_done",
                             read=len(buf),
                             accepted=a,
                             skipped=s,
                             total_accepted=total_accepted,
                             total_skipped=total_skipped,
                             total_read=total_read
                             )
                buf = []

        if buf:
            total_read += len(buf)
            if dry_run:
                log.info(
                    "import_batch_dry",
                    read=len(buf),
                    total_read=total_read
                )
            else:
                a, s = await _process_batch(buf)
                total_accepted += a
                total_skipped += s
                log.info("import_batch_done",
                         read=len(buf),
                         accepted=a,
                         skipped=s,
                         total_accepted=total_accepted,
                         total_skipped=total_skipped,
                         total_read=total_read
                         )

    log.info(
        "import_complete",
        total_read=total_read,
        total_accepted=total_accepted,
        total_skipped=total_skipped
    )


def main():
    parser = argparse.ArgumentParser(
        description="Import events from CSV (idempotent)."
    )
    parser.add_argument("path", help="Path to CSV file")
    parser.add_argument(
        "--batch-size",
        type=int,
        default=5000,
        help="Rows per DB batch"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Read file but do not write to DB"
    )
    args = parser.parse_args()

    asyncio.run(_run(args.path, args.batch_size, args.dry_run))


if __name__ == "__main__":
    main()
