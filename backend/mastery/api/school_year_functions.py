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


def _get_value(entity, name: str):
    """
    Get a value by name from either a dict or a Django model instance.
    """
    if isinstance(entity, dict):
        return entity.get(name)
    return getattr(entity, name, None)


def is_group_from_school_year(group, school_year: str) -> bool:
    """
    Check if a group is from the specified school year based on its valid_from and valid_to dates.
    """
    valid_from_str = _get_value(group, "valid_from")
    valid_to_str = _get_value(group, "valid_to")
    if not valid_from_str or not valid_to_str:
        return False

    try:
        valid_from = datetime.fromisoformat(valid_from_str)
        valid_to = datetime.fromisoformat(valid_to_str)
    except ValueError:
        return False

    start_year, end_year = map(int, school_year.split("-"))
    return (
        valid_from.year == start_year and
        valid_to.year == end_year
    )


# use created_at, for groups, return is_group_from_school_year instead
def is_entity_from_school_year(entity, school_year: str) -> bool:
    if _get_value(entity, "valid_from") and _get_value(entity, "valid_to"):
        return is_group_from_school_year(entity, school_year)

    try:
        created_at = datetime.fromisoformat(_get_value(entity, "created_at"))
    except ValueError:
        return False

    start_year, end_year = map(int, school_year.split("-"))
    return (
        (created_at.year == start_year and created_at.month >= START_MONTH) or
        (created_at.year == end_year and created_at.month <= END_MONTH)
    )
