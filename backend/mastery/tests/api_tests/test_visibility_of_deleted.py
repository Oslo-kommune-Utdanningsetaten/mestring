import pytest
from django.utils import timezone
from rest_framework.test import APIClient
from mastery.models import Group

# These tests verify visibility of soft-deleted groups and users, via the API
# Even though all relevant viewssets obey the is_deleted filter, only user and group tests have been implemented


@pytest.fixture
def set_up_database(db):
    print("Setting up database")


@pytest.mark.django_db
def test_non_deleted_group_access(
        school, student, teacher, superadmin, teacher_role, student_role):

    group = Group.objects.create(
        feide_id="fc:group:some-basis-group",
        display_name="Klasse 7a",
        type="basis",
        school=school,
        is_enabled=True,
        marked_for_deletion_at=None
    )

    group.add_member(teacher, teacher_role)
    group.add_member(student, student_role)

    client = APIClient()
    for user in [superadmin, teacher, student]:
        client.force_authenticate(user=user)

        # Can list the group
        resp = client.get('/api/groups/', {'school': school.id})
        assert resp.status_code == 200
        data = resp.json()
        expected_ids = {group.id}
        received_ids = {group['id'] for group in data}
        assert expected_ids == received_ids
        # Can retrieve the specific group
        resp = client.get(f'/api/groups/{group.id}/')
        assert resp.status_code == 200


@pytest.mark.django_db
def test_deleted_group_access(
        school, student, teacher, superadmin, teacher_role, student_role):

    group = Group.objects.create(
        feide_id="fc:group:some-basis-group",
        display_name="Klasse 7a",
        type="basis",
        school=school,
        is_enabled=True,
        marked_for_deletion_at=timezone.now()
    )

    group.add_member(teacher, teacher_role)
    group.add_member(student, student_role)

    client = APIClient()
    for user in [superadmin, teacher, student]:
        client.force_authenticate(user=user)

        # List returns empty because the group is deleted
        resp = client.get('/api/groups/', {'school': school.id})
        assert resp.status_code == 200
        assert resp.json() == []

        # Cannot retrieve the specific group because it's deleted
        resp = client.get(f'/api/groups/{group.id}/')
        data = resp.json()
        assert resp.status_code == 404

        # Can list the group when including deleted param
        resp = client.get('/api/groups/', {'school': school.id, 'isDeleted': True})
        assert resp.status_code == 200
        expected_ids = {group.id}
        received_ids = {group['id'] for group in resp.json()}
        assert expected_ids == received_ids

        # Can retrieve the specific group when including deleted param
        resp = client.get(f'/api/groups/{group.id}/', {'isDeleted': True})
        assert resp.status_code == 200
        assert resp.json()['id'] == group.id


@pytest.mark.django_db
def test_non_deleted_user_access(school, student, superadmin, teaching_group, student_role):

    teaching_group.add_member(student, student_role)
    student.marked_for_deletion_at = None
    student.save()

    client = APIClient()
    client.force_authenticate(user=superadmin)

    # Can list the user
    resp = client.get('/api/users/', {'school': school.id})
    assert resp.status_code == 200
    expected_ids = {student.id}
    received_ids = {student['id'] for student in resp.json()}
    assert expected_ids == received_ids

    # Can retrieve the specific user
    resp = client.get(f'/api/users/{student.id}/')
    assert resp.status_code == 200


@pytest.mark.django_db
def test_deleted_user_access(school, student, superadmin, teaching_group, student_role):

    teaching_group.add_member(student, student_role)
    student.marked_for_deletion_at = timezone.now()
    student.save()

    client = APIClient()
    client.force_authenticate(user=superadmin)

    # Cannot list deleted user
    resp = client.get('/api/users/', {'school': school.id})
    assert resp.status_code == 200
    assert resp.json() == []

    # Can retrieve the deleted user
    resp = client.get(f'/api/users/{student.id}/')
    assert resp.status_code == 404

    # Can list the user with deleted param
    resp = client.get('/api/users/', {'school': school.id, 'isDeleted': True})
    assert resp.status_code == 200
    expected_ids = {student.id}
    received_ids = {student['id'] for student in resp.json()}
    assert expected_ids == received_ids

    # Can retrieve the user with deleted param
    resp = client.get(f'/api/users/{student.id}/', {'isDeleted': True})
    assert resp.status_code == 200
