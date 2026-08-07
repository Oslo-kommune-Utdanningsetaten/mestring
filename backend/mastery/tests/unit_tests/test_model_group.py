import pytest
from django.utils import timezone
from mastery.models import Group


@pytest.mark.django_db
def test_within_validity_period_includes_valid_groups(school):
    """Groups with valid_from <= now <= valid_to should be within the validity period."""
    now = timezone.now()
    valid_group = Group.objects.create(
        feide_id="fc:group:valid-group",
        display_name="Valid group",
        type="teaching",
        school=school,
        is_enabled=True,
        valid_from=now - timezone.timedelta(days=3),
        valid_to=now + timezone.timedelta(days=3),
    )

    result = Group.objects.within_validity_period()

    assert result.count() == 1
    assert result.first().id == valid_group.id


@pytest.mark.django_db
def test_within_validity_period_includes_group_with_no_valid_from(school):
    """Groups with no valid_from and valid_to in the future should be valid."""
    now = timezone.now()
    valid_group = Group.objects.create(
        feide_id="fc:group:no-valid-from",
        display_name="No valid from",
        type="teaching",
        school=school,
        is_enabled=True,
        valid_from=None,
        valid_to=now + timezone.timedelta(days=3),
    )

    result = Group.objects.within_validity_period()

    assert result.count() == 1
    assert result.first().id == valid_group.id


@pytest.mark.django_db
def test_within_validity_period_includes_group_with_no_valid_to(school):
    """Groups with valid_from in the past and no valid_to should be valid."""
    now = timezone.now()
    valid_group = Group.objects.create(
        feide_id="fc:group:no-valid-to",
        display_name="No valid to",
        type="teaching",
        school=school,
        is_enabled=True,
        valid_from=now - timezone.timedelta(days=3),
        valid_to=None,
    )

    result = Group.objects.within_validity_period()

    assert result.count() == 1
    assert result.first().id == valid_group.id


@pytest.mark.django_db
def test_within_validity_period_includes_group_with_no_validity_window(school):
    """Groups with neither valid_from nor valid_to should be valid."""
    valid_group = Group.objects.create(
        feide_id="fc:group:no-window",
        display_name="No validity window",
        type="teaching",
        school=school,
        is_enabled=True,
        valid_from=None,
        valid_to=None,
    )

    result = Group.objects.within_validity_period()

    assert result.count() == 1
    assert result.first().id == valid_group.id


@pytest.mark.django_db
def test_within_validity_period_excludes_expired_group(school):
    """Groups with valid_to in the past should be outside the validity period."""
    now = timezone.now()
    Group.objects.create(
        feide_id="fc:group:expired",
        display_name="Expired group",
        type="teaching",
        school=school,
        is_enabled=True,
        valid_from=now - timezone.timedelta(days=3),
        valid_to=now - timezone.timedelta(days=1),
    )

    result = Group.objects.within_validity_period()

    assert result.count() == 0


@pytest.mark.django_db
def test_within_validity_period_excludes_future_group(school):
    """Groups with valid_from in the future should be outside the validity period."""
    now = timezone.now()
    Group.objects.create(
        feide_id="fc:group:future",
        display_name="Future group",
        type="teaching",
        school=school,
        is_enabled=True,
        valid_from=now + timezone.timedelta(days=1),
        valid_to=None,
    )

    result = Group.objects.within_validity_period()

    assert result.count() == 0


@pytest.mark.django_db
def test_within_validity_period_respects_exact_boundaries(school, monkeypatch):
    """Groups exactly at the validity boundaries should be included."""
    now = timezone.now()

    def frozen_now():
        return now

    monkeypatch.setattr(timezone, 'now', frozen_now)

    starts_now = Group.objects.create(
        feide_id="fc:group:starts-now",
        display_name="Starts now",
        type="teaching",
        school=school,
        is_enabled=True,
        valid_from=now,
        valid_to=now + timezone.timedelta(days=3),
    )
    ends_now = Group.objects.create(
        feide_id="fc:group:ends-now",
        display_name="Ends now",
        type="teaching",
        school=school,
        is_enabled=True,
        valid_from=now - timezone.timedelta(days=3),
        valid_to=now,
    )

    result = Group.objects.within_validity_period()

    assert result.count() == 2
    assert {group.id for group in result} == {starts_now.id, ends_now.id}


@pytest.mark.django_db
def test_within_validity_period_mixed_groups(school):
    """Only valid groups should be returned when multiple groups exist."""
    now = timezone.now()
    valid_group = Group.objects.create(
        feide_id="fc:group:valid",
        display_name="Valid group",
        type="teaching",
        school=school,
        is_enabled=True,
        valid_from=now - timezone.timedelta(days=3),
        valid_to=now + timezone.timedelta(days=3),
    )
    Group.objects.create(
        feide_id="fc:group:expired",
        display_name="Expired group",
        type="teaching",
        school=school,
        is_enabled=True,
        valid_from=now - timezone.timedelta(days=3),
        valid_to=now - timezone.timedelta(days=1),
    )
    Group.objects.create(
        feide_id="fc:group:future",
        display_name="Future group",
        type="teaching",
        school=school,
        is_enabled=True,
        valid_from=now + timezone.timedelta(days=1),
        valid_to=None,
    )

    result = Group.objects.within_validity_period()

    assert result.count() == 1
    assert result.first().id == valid_group.id
