import pytest
from rest_framework.test import APIClient

# This test suite should cover all cases where users access shools, no matter which endpoint is used

@pytest.mark.django_db
def test_non_user_school_access(school):
    client = APIClient()
    # Non-authenticated user cannot access schools
    resp = client.get(f'/api/schools/')
    assert resp.status_code == 403
    resp = client.get(f'/api/schools/{school.id}/')
    assert resp.status_code == 403

@pytest.mark.django_db
def test_superadmin_school_access(superadmin, school, other_school):
    client = APIClient()
    client.force_authenticate(user=superadmin)

    # Can list all schools
    resp = client.get('/api/schools/')
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    ids = {school['id'] for school in data}
    assert school.id in ids
    assert other_school.id in ids

    # Retrieving schools by ID
    resp = client.get(f'/api/schools/{school.id}/')
    assert resp.status_code == 200
    resp = client.get(f'/api/schools/{other_school.id}/')
    assert resp.status_code == 200

@pytest.mark.django_db
def test_user_school_access(teaching_group_with_members, school, other_school):
    client = APIClient()
    teacher = teaching_group_with_members.get_teachers().first()
    student = teaching_group_with_members.get_students().first()
    for user in [teacher, student]:
        client.force_authenticate(user=user)
        # List shows only own school
        resp = client.get('/api/schools/')
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        ids = {school['id'] for school in data}
        assert school.id in ids
        assert other_school.id not in ids

        # Retrieving schools by ID
        resp = client.get(f'/api/schools/{school.id}/')
        assert resp.status_code == 200
        resp = client.get(f'/api/schools/{other_school.id}/')
        assert resp.status_code == 404