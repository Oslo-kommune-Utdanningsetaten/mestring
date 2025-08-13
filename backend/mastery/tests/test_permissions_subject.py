import pytest
from rest_framework.test import APIClient
from mastery.models import User, Group


@pytest.mark.django_db
def test_group_subject_access(superadmin, school, other_school):
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
def test_wned_subject_access(teaching_group_with_members, school, other_school):
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