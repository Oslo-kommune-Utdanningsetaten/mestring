import pytest
from datetime import datetime
from django.utils import timezone

from mastery.api.school_year_functions import is_entity_from_school_year
from mastery.models import Group


@pytest.mark.django_db
def test_is_entity_from_school_year_accepts_model_instance(school):
    """is_entity_from_school_year should work with Django model instances using datetime created_at."""
    current_school_year = "2026-2027"

    group = Group.objects.create(
        feide_id="fc:group:current-year-group",
        display_name="Current year group",
        type="teaching",
        school=school,
        is_enabled=True,
    )

    assert is_entity_from_school_year(group, current_school_year) is True


def test_is_entity_from_school_year_accepts_api_dict():
    """is_entity_from_school_year should work with API payload dicts containing string created_at."""
    current_school_year = "2026-2027"

    observation_dict = {
        "created_at": "2026-09-01T12:00:00",
    }

    assert is_entity_from_school_year(observation_dict, current_school_year) is True
