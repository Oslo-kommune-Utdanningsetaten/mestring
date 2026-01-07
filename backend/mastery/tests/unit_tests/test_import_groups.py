import pytest
from mastery.data_import.import_groups import import_groups
from mastery import models
from django.utils import timezone


@pytest.mark.django_db
def test_import_groups_create(groups_data, school):
    """Test group creation on import"""

    # Import creates basis and teaching groups, and required subject
    result = list(import_groups(groups_data))
    final_chunk = result[-1]
    assert final_chunk["is_done"] is True
    changes = final_chunk["result"]["changes"]
    assert changes["basis_group"]["created"] == 1
    assert changes["basis_group"]["maintained"] == 0
    assert changes["teaching_group"]["created"] == 1
    assert changes["teaching_group"]["maintained"] == 0
    assert changes["subject"]["created"] == 1
    assert changes["subject"]["maintained"] == 0
    teaching_group = models.Group.objects.get(feide_id=groups_data["teaching"][0]["id"])
    basis_group = models.Group.objects.get(feide_id=groups_data["basis"][0]["id"])
    subject = models.Subject.objects.get(grep_code=groups_data["teaching"][0]["grep"]["code"])
    assert teaching_group
    assert basis_group
    assert subject


@pytest.mark.django_db
def test_import_groups_maintain(groups_data, school):
    """Test group maintenance on import"""
    # Initial import creates basis and teaching groups, and required subject
    result = list(import_groups(groups_data))
    # Re-importing with same data maintains existing data
    result = list(import_groups(groups_data))
    final_chunk = result[-1]
    assert final_chunk["is_done"] is True
    changes = final_chunk["result"]["changes"]
    assert changes["basis_group"]["created"] == 0
    assert changes["basis_group"]["maintained"] == 1
    assert changes["teaching_group"]["created"] == 0
    assert changes["teaching_group"]["maintained"] == 1
    assert changes["subject"]["created"] == 0
    assert changes["subject"]["maintained"] == 1
    # get fresh rows from db
    teaching_group = models.Group.objects.get(feide_id=groups_data["teaching"][0]["id"])
    basis_group = models.Group.objects.get(feide_id=groups_data["basis"][0]["id"])
    subject = models.Subject.objects.get(grep_code=groups_data["teaching"][0]["grep"]["code"])

    assert teaching_group.created_at < teaching_group.maintained_at
    assert basis_group.created_at < basis_group.maintained_at
    assert subject.created_at < subject.maintained_at


@pytest.mark.django_db
def test_import_groups_undelete(groups_data, school):
    """Test undelete on import"""
    # Initial import creates basis and teaching groups, and required subject
    list(import_groups(groups_data))
    teaching_group = models.Group.objects.get(feide_id=groups_data["teaching"][0]["id"])
    deleted_ts = timezone.now() - timezone.timedelta(days=1)
    # Soft-delete teaching group and a related goal
    goal = models.Goal.objects.create(title="Lese bøk. Les bøk!",
                                      group=teaching_group, deleted_at=deleted_ts, school=school)
    teaching_group.deleted_at = deleted_ts
    teaching_group.save()
    # Re-importing with same data will undelete soft-deleted groups and their goals
    list(import_groups(groups_data))
    teaching_group.refresh_from_db()
    goal.refresh_from_db()
    assert teaching_group.deleted_at is None
    assert goal.deleted_at is None
