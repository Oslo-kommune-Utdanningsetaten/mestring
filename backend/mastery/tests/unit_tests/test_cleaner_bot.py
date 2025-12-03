import pytest
from mastery.data_import.cleaner_bot import update_data_integrity
from mastery import models
from django.utils import timezone


@pytest.fixture
def valid_group(school):
    now = timezone.now()
    return models.Group.objects.create(
        feide_id="fc:group:some-basis-group-valid",
        display_name="Klasse 7a",
        type="basis",
        school=school,
        is_enabled=True,
        deleted_at=None,
        valid_from=now - timezone.timedelta(days=3),
        valid_to=now + timezone.timedelta(days=1)
    )


@pytest.fixture
def invalid_group(school):
    now = timezone.now()
    return models.Group.objects.create(
        feide_id="fc:group:some-basis-group-invalid",
        display_name="Klasse 7a",
        type="basis",
        school=school,
        is_enabled=True,
        deleted_at=None,
        valid_from=now - timezone.timedelta(days=3),
        valid_to=now - timezone.timedelta(days=1)
    )


@pytest.mark.django_db
def test_soft_delete_unmaintained_valid_group(valid_group):
    now = timezone.now()

    # unmaintained valid group should be soft-deleted
    valid_group.maintained_at = now - timezone.timedelta(days=10)
    valid_group.save()
    result = update_data_integrity(now)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    valid_group.refresh_from_db()
    assert final_chunk["is_done"] is True
    assert changes["group"]["soft-deleted"] == 1
    assert valid_group.deleted_at is not None

    # unmaintained, deleted group should not be handled
    previous_deleted_at = valid_group.deleted_at
    result = update_data_integrity(now)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    valid_group.refresh_from_db()
    assert final_chunk["is_done"] is True
    assert changes["group"]["soft-deleted"] == 0
    assert valid_group.deleted_at == previous_deleted_at


@pytest.mark.django_db
def test_soft_delete_unmaintained_invalid_group(invalid_group):
    now = timezone.now()
    invalid_group.maintained_at = now - timezone.timedelta(days=10)
    invalid_group.save()
    result = update_data_integrity(now)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    invalid_group.refresh_from_db()
    # unmaintained invalid group should not be soft-deleted
    assert final_chunk["is_done"] is True
    assert changes["group"]["soft-deleted"] == 0
    assert invalid_group.deleted_at is None


@pytest.mark.django_db
def test_keep_maintained_user(student):
    now = timezone.now()
    # Don't soft-delete maintained user
    student.maintained_at = now
    student.save()
    result = update_data_integrity(now)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    student.refresh_from_db()
    assert final_chunk["is_done"] is True
    assert changes["user"]["soft-deleted"] == 0
    assert student.deleted_at is None


@pytest.mark.django_db
def test_soft_delete_unmaintained_user(student):
    now = timezone.now()
    # Soft-delete unmaintained user without active memberships
    student.maintained_at = now - timezone.timedelta(days=10)
    student.save()
    result = update_data_integrity(now)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    student.refresh_from_db()
    assert final_chunk["is_done"] is True
    assert changes["user"]["soft-deleted"] == 1
    assert student.deleted_at is not None


@pytest.mark.django_db
def test_keep_user_with_membership(student, student_role, valid_group):
    now = timezone.now()
    # Don't soft-delete user with active memberships
    valid_group.add_member(student, student_role)
    student.save()
    result = update_data_integrity(now)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    student.refresh_from_db()
    assert final_chunk["is_done"] is True
    assert changes["user"]["soft-deleted"] == 0
    assert student.deleted_at is None


@pytest.mark.django_db
def test_keep_superadmin_user(student):
    now = timezone.now()
    # Don't soft-delete superadmin
    student.is_superadmin = True  # unlikely for a student, but hey
    student.save()
    result = update_data_integrity(now)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    student.refresh_from_db()
    assert final_chunk["is_done"] is True
    assert changes["user"]["soft-deleted"] == 0
    assert student.deleted_at is None
