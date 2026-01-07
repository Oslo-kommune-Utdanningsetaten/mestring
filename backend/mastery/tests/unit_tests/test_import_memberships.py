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
    result = list(import_memberships(memberships_data))
    final_chunk = result[-1]
    assert final_chunk["is_done"] is True
    changes = final_chunk["result"]["changes"]
    assert changes["user"]["created"] == 5
    assert changes["user"]["maintained"] == 0
    assert changes["membership"]["created"] == 6
    assert changes["membership"]["maintained"] == 0
    assert models.User.objects.all().count() == 5
    teacher_feide_id = memberships_data[f"{a_teaching_group.feide_id}"]["teachers"][0]["feide_id"]
    assert models.User.objects.filter(feide_id=teacher_feide_id).exists()


@pytest.mark.django_db
def test_import_users_maintain(memberships_data, school, a_teaching_group, a_basis_group):
    """Test user maintenance on import"""
    # Initial import creates users
    result = list(import_memberships(memberships_data))
    # Re-mporting with same data maintains existing data
    result = list(import_memberships(memberships_data))
    final_chunk = result[-1]
    changes = final_chunk["result"]["changes"]
    assert final_chunk["is_done"] is True
    assert changes["user"]["created"] == 0
    assert changes["user"]["maintained"] == 5
    assert changes["membership"]["created"] == 0
    assert changes["membership"]["maintained"] == 6
    assert models.User.objects.all().count() == 5
    # get fresh rows from db
    teacher_feide_id = memberships_data[f"{a_teaching_group.feide_id}"]["teachers"][0]["feide_id"]
    teacher = models.User.objects.filter(feide_id=teacher_feide_id).first()
    assert teacher.created_at < teacher.maintained_at


@pytest.mark.django_db
def test_import_users_undelete(memberships_data, school, a_teaching_group, a_basis_group):
    """Test undelete on import"""
    # Initial import creates users
    list(import_memberships(memberships_data))
    # Soft-delete a user and a membership
    user_feide_id = memberships_data[f"{a_teaching_group.feide_id}"]["students"][0]["feide_id"]
    user = models.User.objects.filter(feide_id=user_feide_id).first()
    user.deleted_at = timezone.now()
    user.save()
    # Re-importing with same data should undelete the user and membership
    list(import_memberships(memberships_data))
    user.refresh_from_db()
    assert user.deleted_at is None


@pytest.mark.django_db
def test_import_memberships_undelete(memberships_data, school, a_teaching_group, a_basis_group):
    """Test undelete of memberships on import"""
    # Initial import creates users and memberships
    list(import_memberships(memberships_data))
    teacher_feide_id = memberships_data[f"{a_teaching_group.feide_id}"]["teachers"][0]["feide_id"]
    teacher = models.User.objects.filter(feide_id=teacher_feide_id).first()
    user_group = models.UserGroup.objects.filter(user=teacher, group=a_teaching_group).first()
    assert user_group is not None
    user_group.deleted_at = timezone.now()
    user_group.save()
    # Re-importing with same data should undelete the membership
    list(import_memberships(memberships_data))
    user_group.refresh_from_db()
    assert user_group.created_at < user_group.maintained_at
    assert user_group.deleted_at is None
