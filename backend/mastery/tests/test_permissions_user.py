import pytest
from rest_framework.test import APIClient
from mastery.models import User, Group

@pytest.mark.django_db
def test_non_user_user_access(school, teaching_group_with_members, teacher, student):
    client = APIClient()
    # Non-authenticated user cannot access any users
    resp = client.get('/api/users/')
    assert resp.status_code == 403
    resp = client.get(f'/api/users/{teacher.id}/')
    assert resp.status_code == 403
    resp = client.get(f'/api/users/{student.id}/')
    assert resp.status_code == 403

@pytest.mark.django_db
def test_superadmin_user_access(superadmin, school, teacher, student, other_student):
    client = APIClient()
    client.force_authenticate(user=superadmin)

    # Can list all users
    resp = client.get('/api/users/')
    assert resp.status_code == 200
    data = resp.json()
    expected_ids = {superadmin.id, teacher.id, student.id, other_student.id}
    received_ids = {user['id'] for user in data}
    assert len(received_ids) == len(expected_ids)
    assert expected_ids.issubset(received_ids)

@pytest.mark.django_db
def test_superadmin_user_access_via_group(superadmin, teaching_group_with_members):
    client = APIClient()
    client.force_authenticate(user=superadmin)

    # Can retrieve a user
    resp = client.get(f'/api/groups/{teaching_group_with_members.id}/members/')
    assert resp.status_code == 200

@pytest.mark.django_db
def test_user_self_access(teacher, student):
    client = APIClient()

    for user in [teacher, student]:
        client.force_authenticate(user=user)

        resp = client.get('/api/users/')
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]['id'] == user.id

        # User can retrieve self
        resp = client.get(f'/api/users/{user.id}/')
        assert resp.status_code == 200


@pytest.mark.django_db
def test_user_user_access(teacher, student, other_student, teaching_group, roles):
    client = APIClient()
    client.force_authenticate(user=teacher)

    # Teacher cannot retrieve an unrelated student
    resp = client.get(f'/api/users/{student.id}/')
    assert resp.status_code == 404

    # Teacher can retrieve student if in group
    student_role, teacher_role = roles
    teaching_group.add_member(teacher, teacher_role)
    teaching_group.add_member(student, student_role)
    resp = client.get(f'/api/users/{student.id}/')
    assert resp.status_code == 200

    # Teacher can list users in their groups
    resp = client.get('/api/users/')
    assert resp.status_code == 200
    data = resp.json()
    expected_ids = {teacher.id, student.id}
    received_ids = {user['id'] for user in data}
    assert len(received_ids) == len(expected_ids)
    assert expected_ids.issubset(received_ids)

    # Teacher can list users in their groups via groups endpoint
    resp = client.get(f'/api/groups/{teaching_group.id}/members/')
    assert resp.status_code == 200
    data = resp.json()
    expected_ids = {teacher.id, student.id}
    received_ids = {user['id'] for user in data}
    assert len(received_ids) == len(expected_ids)
    assert expected_ids.issubset(received_ids)

    # Student can retrieve self
    client.force_authenticate(user=student)
    resp = client.get(f'/api/users/{student.id}/')
    assert resp.status_code == 200

    # Student can retrieve teacher if in group
    resp = client.get(f'/api/users/{teacher.id}/')
    assert resp.status_code == 200

    # Student can list users in their groups via groups endpoint
    resp = client.get(f'/api/groups/{teaching_group.id}/members/')
    assert resp.status_code == 200
    data = resp.json()
    expected_ids = {teacher.id, student.id}
    received_ids = {user['id'] for user in data}
    assert len(received_ids) == len(expected_ids)
    assert expected_ids.issubset(received_ids)

    # Student cannot retrieve unrelated other student
    resp = client.get(f'/api/users/{other_student.id}/')
    assert resp.status_code == 404

    # Student can list users in their groups
    resp = client.get('/api/users/')
    assert resp.status_code == 200
    data = resp.json()
    expected_ids = {teacher.id, student.id}
    received_ids = {user['id'] for user in data}
    assert len(received_ids) == len(expected_ids)
    assert expected_ids.issubset(received_ids)

    # Student cannot retrieve an unrelated student
    resp = client.get(f'/api/users/{other_student.id}/')
    assert resp.status_code == 404

    # other student cannot access teacher or student
    client.force_authenticate(user=other_student)
    resp = client.get(f'/api/users/{teacher.id}/')
    assert resp.status_code == 404
    resp = client.get(f'/api/users/{student.id}/')
    assert resp.status_code == 404

    # Unrelated other student cannot list users via groups endpoint
    resp = client.get(f'/api/groups/{teaching_group.id}/members/')
    assert resp.status_code == 404
