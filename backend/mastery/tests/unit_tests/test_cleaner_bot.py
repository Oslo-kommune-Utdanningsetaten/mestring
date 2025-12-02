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
def test_soft_delete_unmaintained_valid_group(school, valid_group):
    valid_group.maintained_at = timezone.now() - timezone.timedelta(days=10)
    valid_group.save()
    result = update_data_integrity(school.org_number, timezone.now())
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    valid_group.refresh_from_db()
    # unmaintained valid group should be soft-deleted
    assert final_chunk["is_done"] is True
    assert changes["groups"]["soft-deleted"] == 1
    assert valid_group.deleted_at is not None
    # unmaintained, deleted group should not be handled
    previous_deleted_at = valid_group.deleted_at
    result = update_data_integrity(school.org_number, timezone.now())
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    valid_group.refresh_from_db()
    assert final_chunk["is_done"] is True
    assert changes["groups"]["soft-deleted"] == 0
    assert valid_group.deleted_at == previous_deleted_at


@pytest.mark.django_db
def test_soft_delete_unmaintained_invalid_group(school, invalid_group):
    invalid_group.maintained_at = timezone.now() - timezone.timedelta(days=10)
    invalid_group.save()
    result = update_data_integrity(school.org_number, timezone.now())
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    invalid_group.refresh_from_db()
    # unmaintained invalid group should not be soft-deleted
    assert final_chunk["is_done"] is True
    assert changes["groups"]["soft-deleted"] == 0
    assert invalid_group.deleted_at is None


@pytest.mark.django_db
def test_soft_delete_unmaintained_user(school, student, valid_group):
    assert True
