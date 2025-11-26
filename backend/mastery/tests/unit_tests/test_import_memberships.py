import pytest
from mastery.data_import.import_users import import_memberships
from mastery import models
from django.utils import timezone


@pytest.fixture
def memberships_data(db, groups_data):
    teaching_goup_id = groups_data["teaching"][0]["id"]
    basis_goup_id = groups_data["basis"][0]["id"]
    return {
        f"{teaching_goup_id}": {
            "teachers": [
                {
                    "feide_id": "janne@feide.osloskolen.no",
                    "name": "Janne Lerke",
                    "email": "janne@osloskolen.no",
                    "affiliation": "faculty"
                },
            ],
            "students": [
                {
                    "feide_id": "frank@feide.osloskolen.no",
                    "name": "Frank Larsen",
                    "email": "frank@osloskolen.no",
                    "affiliation": "student"
                },
                {
                    "feide_id": "mia@feide.osloskolen.no",
                    "name": "Mia Zolovich",
                    "email": "mia@osloskolen.no",
                    "affiliation": "student"
                }
            ],
            "other": []
        },
        f"{basis_goup_id}": {
            "teachers": [
                {
                    "feide_id": "fjodor@feide.osloskolen.no",
                    "name": "Fjodor Wigwam",
                    "email": "fjodor@osloskolen.no",
                    "affiliation": "faculty"
                },
            ],
            "students": [
                {
                    "feide_id": "frank@feide.osloskolen.no",
                    "name": "Frank Larsen",
                    "email": "frank@osloskolen.no",
                    "affiliation": "student"
                },
                {
                    "feide_id": "mildred@feide.osloskolen.no",
                    "name": "Mildred Hansen",
                    "email": "mildred@osloskolen.no",
                    "affiliation": "student"
                },
            ]
        }
    }


@pytest.fixture
def a_teaching_group(db, school, groups_data):
    return models.Group.objects.create(
        feide_id=groups_data["teaching"][0]["id"],
        display_name=groups_data["teaching"][0]["displayName"],
        type="teaching",
        school=school,
        is_enabled=True
    )


@pytest.fixture
def a_basis_group(db, school, groups_data):
    return models.Group.objects.create(
        feide_id=groups_data["basis"][0]["id"],
        display_name=groups_data["basis"][0]["displayName"],
        type="basis",
        school=school,
        is_enabled=True
    )


@pytest.mark.django_db
def test_import_users_create(memberships_data, school, a_teaching_group, a_basis_group):
    """Test user creation on import"""

    # Import creates users and memberships
    result = list(import_memberships(memberships_data))
    final_chunk = result[-1]
    assert final_chunk["is_done"] is True
    changes = final_chunk["result"]["changes"]
    assert changes["user"]["created"] == 5
    assert changes["user"]["maintained"] == 0
    assert changes["membership"]["created"] == 6
    assert changes["membership"]["maintained"] == 0
