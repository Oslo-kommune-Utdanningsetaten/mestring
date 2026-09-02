from datetime import date, datetime
from typing import Optional, TypedDict

from django.utils import timezone


# school year start
START_MONTH = 8  # august
START_DAY = 1  # first day of august
# school year midyear
MIDYEAR_MONTH = 1  # january
MIDYEAR_DAY = 15  # fifteenth day of january
# school year end
END_MONTH = 7  # july
END_DAY = 31  # thirty-first day of july


class SchoolYearMilestones(TypedDict):
    start_at: date
    midyear_at: date
    end_at: date


def calculate_milestones(custom_date: Optional[date | datetime] = None) -> SchoolYearMilestones:
    if custom_date is None:
        custom_date = timezone.now()

    if isinstance(custom_date, datetime):
        custom_date = custom_date.date()

    year = custom_date.year
    month = custom_date.month
    school_start_year = year - 1 if month < START_MONTH else year

    return {
        "start_at": date(school_start_year, START_MONTH, START_DAY),
        "midyear_at": date(school_start_year + 1, MIDYEAR_MONTH, MIDYEAR_DAY),
        "end_at": date(school_start_year + 1, END_MONTH, END_DAY),
    }


def get_current_school_year() -> str:
    milestones = calculate_milestones()
    start_year = milestones["start_at"].year
    end_year = milestones["end_at"].year
    return f"{start_year}-{end_year}"


# Check if the entity belongs to the specified school year based on its created_at
# For groups, use group.is_valid (which checks validFrom and validTo) instead of created_at
def is_entity_from_school_year(entity, school_year: str) -> bool:
    try:
        if isinstance(entity, dict):
            created_at = entity.get("created_at")
            created_at = datetime.fromisoformat(created_at)
        else:
            created_at = getattr(entity, "created_at", None)

    except ValueError:
        return False

    start_year, end_year = map(int, school_year.split("-"))
    return (
        (created_at.year == start_year and created_at.month >= START_MONTH) or
        (created_at.year == end_year and created_at.month <= END_MONTH)
    )


def is_entity_from_current_school_year(entity) -> bool:
    # just a convenience wrapper
    current_school_year = get_current_school_year()
    return is_entity_from_school_year(entity, current_school_year)
