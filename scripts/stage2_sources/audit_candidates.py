"""Offline structural audit of a locally held, authorized VOC candidate CSV.

This script prints counts and errors only. It never uploads or prints review text.
It does not decide whether a review directly discusses Duolingo Video Call.
"""

import argparse
import csv
from datetime import datetime, timezone
from math import isfinite
from pathlib import Path
from urllib.parse import urlparse


REQUIRED = (
    "platform", "product", "app_id", "record_id", "source_url",
    "url_granularity", "source_date", "source_date_type", "accessed_on",
    "country", "language", "sampling_mode", "query_or_sort", "title",
    "text", "score",
)
PERSONAL_FIELDS = {"username", "user_name", "author", "user_id", "profile_url", "userurl"}


def parse_date(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed


def audit(path: Path) -> tuple[dict, list[str]]:
    errors: list[str] = []
    counts = {"rows": 0, "unique_keys": 0, "duplicate_keys": 0,
              "unknown_dates": 0, "listing_only_urls": 0, "platforms": {}}
    seen: set[tuple[str, str, str]] = set()
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = reader.fieldnames or []
        missing = sorted(set(REQUIRED) - set(columns))
        personal = sorted(PERSONAL_FIELDS & {c.lower() for c in columns})
        if missing:
            return counts, [f"missing columns: {', '.join(missing)}"]
        if personal:
            return counts, [f"unnecessary personal fields: {', '.join(personal)}"]
        now = datetime.now(timezone.utc)
        for line, row in enumerate(reader, start=2):
            if None in row:
                errors.append(f"line {line}: more fields than header")
            row = {key: (value or "") for key, value in row.items() if key is not None}
            counts["rows"] += 1
            platform = row["platform"].strip()
            counts["platforms"][platform] = counts["platforms"].get(platform, 0) + 1
            for field in ("platform", "product", "app_id", "record_id", "source_url",
                          "accessed_on", "sampling_mode", "query_or_sort", "text"):
                if not (row[field] or "").strip():
                    errors.append(f"line {line}: empty {field}")
            key = (platform, row["app_id"].strip(), row["record_id"].strip())
            if key in seen:
                counts["duplicate_keys"] += 1
                errors.append(f"line {line}: duplicate platform/app_id/record_id")
            seen.add(key)
            url = urlparse(row["source_url"])
            if url.scheme != "https" or not url.netloc:
                errors.append(f"line {line}: source_url must be an HTTPS URL")
            granularity = row["url_granularity"].strip()
            if granularity not in {"item", "listing"}:
                errors.append(f"line {line}: url_granularity must be item or listing")
            if granularity == "listing":
                counts["listing_only_urls"] += 1
            source_date = row["source_date"].strip()
            date_type = row["source_date_type"].strip()
            if not source_date:
                counts["unknown_dates"] += 1
                if date_type != "unknown":
                    errors.append(f"line {line}: empty source_date needs type unknown")
            else:
                if date_type not in {"published", "updated"}:
                    errors.append(f"line {line}: source_date_type must be published or updated")
                try:
                    if parse_date(source_date) > now:
                        errors.append(f"line {line}: source_date is in the future")
                except ValueError:
                    errors.append(f"line {line}: invalid source_date")
            try:
                if parse_date(row["accessed_on"].strip()) > now:
                    errors.append(f"line {line}: accessed_on is in the future")
            except ValueError:
                errors.append(f"line {line}: invalid accessed_on")
            score = row["score"].strip()
            if score:
                try:
                    parsed_score = float(score)
                    if not isfinite(parsed_score) or not 1 <= parsed_score <= 5:
                        errors.append(f"line {line}: score outside 1-5")
                except ValueError:
                    errors.append(f"line {line}: invalid score")
    counts["unique_keys"] = len(seen)
    if not counts["rows"]:
        errors.append("no candidate rows")
    return counts, errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path)
    args = parser.parse_args()
    counts, errors = audit(args.csv_path)
    print(counts)
    for error in errors:
        print(error)
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
