import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_non_user_role_access(student_role, teacher_role):
    client = APIClient()
    # Non-authenticated user cannot access roles
    resp = client.get(f'/api/roles/')
    assert resp.status_code == 403
    resp = client.get(f'/api/roles/{student_role.id}/')
    assert resp.status_code == 403
    resp = client.get(f'/api/roles/{teacher_role.id}/')
    assert resp.status_code == 403


@pytest.mark.django_db
def test_superadmin_role_access(superadmin, student_role, teacher_role):
    client = APIClient()
    client.force_authenticate(user=superadmin)

    # Can list all roles
    resp = client.get('/api/roles/')
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    expected_roles = {student_role.id, teacher_role.id}
    assert expected_roles.issubset({role['id'] for role in data})

    # Retrieving roles by ID
    resp = client.get(f'/api/roles/{student_role.id}/')
    assert resp.status_code == 200
    resp = client.get(f'/api/roles/{teacher_role.id}/')
    assert resp.status_code == 200


@pytest.mark.django_db
def test_user_role_access(student_role, teacher_role, teacher, student):
    client = APIClient()
    for user in [teacher, student]:
        client.force_authenticate(user=user)
        # Can list all roles
        resp = client.get('/api/roles/')
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        expected_roles = {student_role.id, teacher_role.id}
        assert expected_roles.issubset({role['id'] for role in data})

        # Retrieving roles by ID
        resp = client.get(f'/api/roles/{student_role.id}/')
        assert resp.status_code == 200
        resp = client.get(f'/api/roles/{teacher_role.id}/')
        assert resp.status_code == 200
