import pytest
from django.utils import timezone
from rest_framework.test import APIClient
from mastery.models import Group

# These tests verify visibility of soft-deleted groups and users, via the API


@pytest.fixture
def set_up_database(db):
    print("Setting up database")


@pytest.mark.django_db
def test_valid_group_access(
        school, student, teacher, superadmin, teacher_role, student_role):
    now = timezone.now()
    valid_group = Group.objects.create(
        feide_id="fc:group:some-basis-group-1",
        display_name="Klasse 7a",
        type="basis",
        school=school,
        is_enabled=True,
        deleted_at=None,
        valid_from=now - timezone.timedelta(days=3),
        valid_to=now + timezone.timedelta(days=3)
    )
    valid_group_no_from = Group.objects.create(
        feide_id="fc:group:some-basis-group-2",
        display_name="Klasse 7a",
        type="basis",
        school=school,
        is_enabled=True,
        deleted_at=None,
        valid_to=now + timezone.timedelta(days=3)
    )
    valid_group_no_to = Group.objects.create(
        feide_id="fc:group:some-basis-group-3",
        display_name="Klasse 7a",
        type="basis",
        school=school,
        is_enabled=True,
        deleted_at=None,
        valid_from=now - timezone.timedelta(days=3)
    )

    for group in [valid_group, valid_group_no_from, valid_group_no_to]:
        group.add_member(teacher, teacher_role)
        group.add_member(student, student_role)

    client = APIClient()
    for user in [superadmin, teacher, student]:
        client.force_authenticate(user=user)

        # Can list the group
        resp = client.get('/api/groups/', {'school': school.id})
        assert resp.status_code == 200
        data = resp.json()
        expected_ids = {valid_group.id, valid_group_no_from.id, valid_group_no_to.id}
        received_ids = {group['id'] for group in data}
        assert expected_ids == received_ids
        # Can retrieve a specific group
        resp = client.get(f'/api/groups/{valid_group.id}/')
        assert resp.status_code == 200


@pytest.mark.django_db
def test_invalid_group_access(
        school, student, teacher, superadmin, teacher_role, student_role):
    now = timezone.now()
    invalid_group = Group.objects.create(
        feide_id="fc:group:some-basis-group-1",
        display_name="Klasse 7a",
        type="basis",
        school=school,
        is_enabled=True,
        deleted_at=None,
        valid_from=now - timezone.timedelta(days=3),
        valid_to=now - timezone.timedelta(days=1)  # expired
    )
    invalid_group_no_from = Group.objects.create(
        feide_id="fc:group:some-basis-group-2",
        display_name="Klasse 7a",
        type="basis",
        school=school,
        is_enabled=True,
        deleted_at=None,
        valid_to=now - timezone.timedelta(days=3)
    )
    invalid_group_no_to = Group.objects.create(
        feide_id="fc:group:some-basis-group-3",
        display_name="Klasse 7a",
        type="basis",
        school=school,
        is_enabled=True,
        deleted_at=None,
        valid_from=now + timezone.timedelta(days=1)  # valid from tomorrow
    )

    for group in [invalid_group, invalid_group_no_from, invalid_group_no_to]:
        group.add_member(teacher, teacher_role)
        group.add_member(student, student_role)

    client = APIClient()
    for user in [superadmin, teacher, student]:
        client.force_authenticate(user=user)

        # List returns empty because the group is invalid
        resp = client.get('/api/groups/', {'school': school.id})
        assert resp.status_code == 200
        assert len(resp.json()) == 0

        # Cannot retrieve the specific group because it's invalid
        resp = client.get(f'/api/groups/{invalid_group.id}/')
        assert resp.status_code == 404

        # Can list the group when including isValid param
        resp = client.get('/api/groups/', {'school': school.id, 'isValid': False})
        assert resp.status_code == 200
        expected_ids = {invalid_group.id, invalid_group_no_from.id, invalid_group_no_to.id}
        received_ids = {group['id'] for group in resp.json()}
        assert expected_ids == received_ids

        # Can retrieve the specific group when including isValid param
        resp = client.get(f'/api/groups/{invalid_group.id}/', {'isValid': False})
        assert resp.status_code == 200
        assert resp.json()['id'] == invalid_group.id
