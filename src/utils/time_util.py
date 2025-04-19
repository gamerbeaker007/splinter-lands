from datetime import datetime, timezone

from dateutil.relativedelta import relativedelta


def time_until(iso_str):
    # Parse input time and get current time in UTC
    target_time = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)

    # Calculate the difference
    delta = relativedelta(target_time, now)

    # Build parts conditionally
    parts = []
    if delta.years:
        parts.append(f"{delta.years} year{'s' if delta.years != 1 else ''}")
    if delta.months:
        parts.append(f"{delta.months} month{'s' if delta.months != 1 else ''}")
    if delta.days:
        parts.append(f"{delta.days} day{'s' if delta.days != 1 else ''}")
    if delta.hours:
        parts.append(f"{delta.hours} hour{'s' if delta.hours != 1 else ''}")
    if delta.minutes:
        parts.append(f"{delta.minutes} minute{'s' if delta.minutes != 1 else ''}")

    return " ".join(parts) if parts else "now"


def calculate_progress(projected_created_date, projected_end_date):
    if not projected_created_date or not projected_end_date:
        return None  # or 0.0, or "Unknown", etc.

    # Convert ISO strings to datetime
    start = datetime.fromisoformat(projected_created_date.replace("Z", "+00:00"))
    end = datetime.fromisoformat(projected_end_date.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)

    # Handle edge cases
    if now <= start:
        return 0.0
    if now >= end:
        return 100.0

    total_duration = (end - start).total_seconds()
    elapsed = (now - start).total_seconds()
    percent_complete = (elapsed / total_duration) * 100

    return round(percent_complete, 2)
