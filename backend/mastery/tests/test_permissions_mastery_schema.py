import pytest
from rest_framework.test import APIClient

# This test suite should cover all cases where users access mastery schemas


@pytest.mark.django_db
def test_non_user_role_access(mastery_schema):
    client = APIClient()
    # Non-authenticated user cannot access mastery schemas
    resp = client.get(f'/api/mastery-schemas/')
    assert resp.status_code == 403
    resp = client.get(f'/api/mastery-schemas/{mastery_schema.id}/')
    assert resp.status_code == 403


@pytest.mark.django_db
def test_superadmin_role_access(superadmin, mastery_schema):
    client = APIClient()
    client.force_authenticate(user=superadmin)

    # Can list all mastery schemas
    resp = client.get('/api/mastery-schemas/')
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    expected_ids = {mastery_schema.id}
    assert expected_ids.issubset({role['id'] for role in data})

    # Retrieving mastery schemas by ID
    resp = client.get(f'/api/mastery-schemas/{mastery_schema.id}/')
    assert resp.status_code == 200


@pytest.mark.django_db
def test_user_role_access(teacher, student, mastery_schema):
    client = APIClient()
    for user in [teacher, student]:
        client.force_authenticate(user=user)
        # Can list all mastery schemas
        resp = client.get('/api/mastery-schemas/')
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        expected_ids = {mastery_schema.id}
        assert expected_ids.issubset({role['id'] for role in data})

        # Retrieving mastery schemas by ID
        resp = client.get(f'/api/mastery-schemas/{mastery_schema.id}/')
        assert resp.status_code == 200
