import csv, uuid, json, argparse
from datetime import datetime, timedelta, timezone
import os
parser = argparse.ArgumentParser()
parser.add_argument("out", help="Path to CSV, e.g. data/events.csv")
parser.add_argument("--rows", type=int, default=5)
args = parser.parse_args()

os.makedirs(os.path.dirname(args.out), exist_ok=True)
start = datetime(2025, 10, 19, 10, 0, tzinfo=timezone.utc)
event_types = ["login", "view", "purchase", "logout"]

with open(args.out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["event_id","occurred_at","user_id","event_type","properties_json"])
    for i in range(args.rows):
        eid = str(uuid.uuid4())
        ts  = (start + timedelta(minutes=5*i)).isoformat().replace("+00:00","Z")
        uid = f"u{i%3+1}"
        et  = event_types[i % len(event_types)]
        props = {"country":"UA"} if et!="purchase" else {"amount": round(10+2.5*i, 2)}
        w.writerow([eid, ts, uid, et, json.dumps(props)])

print(f"Wrote {args.rows} rows to {args.out}")
