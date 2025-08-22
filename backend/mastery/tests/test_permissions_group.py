import pytest
from rest_framework.test import APIClient
from mastery.models import User, Group

# This test suite should cover all cases where users access groups, no matter which endpoint is used

@pytest.mark.django_db
def test_non_user_group_access(school, teaching_group_with_members, teaching_group_without_members):
    client = APIClient()
    # Non-authenticated user cannot access groups
    resp = client.get('/api/groups/')
    assert resp.status_code == 403
    resp = client.get(f'/api/groups/{teaching_group_with_members.id}/')
    assert resp.status_code == 403
    resp = client.get(f'/api/groups/{teaching_group_without_members.id}/')
    assert resp.status_code == 403

@pytest.mark.django_db
def test_school_id_requirement(school, superadmin, teaching_group_with_members):
    client = APIClient()
    client.force_authenticate(user=superadmin)
    # School ID is required for listing groups
    resp = client.get('/api/groups/')
    assert resp.status_code == 400
    # Listing groups with school ID
    resp = client.get('/api/groups/', {'school': school.id})
    assert resp.status_code == 200
    # School not required for retrieving a specific group
    resp = client.get(f'/api/groups/{teaching_group_with_members.id}/')
    assert resp.status_code == 200

@pytest.mark.django_db
def test_superadmin_group_access(school, teaching_group_with_members, other_teaching_group_with_members, superadmin):
    client = APIClient()
    client.force_authenticate(user=superadmin)

    # Can list groups
    resp = client.get('/api/groups/', {'school': school.id})
    assert resp.status_code == 200
    data = resp.json()
    expected_ids = {teaching_group_with_members.id, other_teaching_group_with_members.id}
    received_ids = {group['id'] for group in data}
    assert len(received_ids) == len(expected_ids)
    assert expected_ids.issubset(received_ids)

    # Create another group and verify superadmin sees it too
    a_group = Group.objects.create(
        feide_id="fc:group:other",
        display_name="Nother Group",
        type="basis",
        school=school
    )
    # Group listing should include new group
    resp = client.get('/api/groups/', {'school': school.id})
    assert resp.status_code == 200
    data = resp.json()
    expected_ids = {teaching_group_with_members.id, other_teaching_group_with_members.id, a_group.id}
    received_ids = {group['id'] for group in data}
    assert len(received_ids) == len(expected_ids)
    assert expected_ids.issubset(received_ids)

    # Can retrieve a specific group
    resp = client.get(f'/api/groups/{teaching_group_with_members.id}/')
    assert resp.status_code == 200


@pytest.mark.django_db
def test_teacher_group_access(teaching_group_with_members, other_teaching_group_with_members, teacher, school):
    client = APIClient()
    client.force_authenticate(user=teacher)

    # School ID is required for listing groups
    resp = client.get('/api/groups/')
    assert resp.status_code == 400

    # Teacher can only list own groups
    resp = client.get('/api/groups/', {'school': school.id})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert all(group['id'] == teaching_group_with_members.id for group in data)

    # Teacher can retrieve own group
    resp = client.get(f'/api/groups/{teaching_group_with_members.id}/')
    assert resp.status_code == 200

    # Teacher cannot retrieve other group
    resp = client.get(f'/api/groups/{other_teaching_group_with_members.id}/')
    assert resp.status_code == 403


@pytest.mark.django_db
def test_student_group_access(teaching_group_with_members, other_teaching_group_with_members, school, roles):
    student = teaching_group_with_members.get_students().first()
    student_role, _ = roles
    client = APIClient()
    client.force_authenticate(user=student)

    # School ID is required for listing groups
    resp = client.get('/api/groups/')
    assert resp.status_code == 400

    # Student can only list own groups
    resp = client.get('/api/groups/', {'school': school.id})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert all(group['id'] == teaching_group_with_members.id for group in data)

    # Add student to new groups and verify student does not see it
    a_group = Group.objects.create(
        feide_id="fc:group:other",
        display_name="Other Group",
        type="basis",
        school=school
    )
    a_group.add_member(student, student_role)
    resp = client.get('/api/groups/', {'school': school.id})
    data = resp.json()
    expected_ids = {teaching_group_with_members.id, a_group.id}
    received_ids = {group['id'] for group in data}
    assert len(received_ids) == len(expected_ids)
    assert expected_ids.issubset(received_ids)

    # Student can retrieve own group
    resp = client.get(f'/api/groups/{teaching_group_with_members.id}/')
    assert resp.status_code == 200

    # Student cannot retrieve other group
    resp = client.get(f'/api/groups/{other_teaching_group_with_members.id}/')
    assert resp.status_code == 403
