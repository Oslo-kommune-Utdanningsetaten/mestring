import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_non_user_mastery_schema_access(mastery_schema):
    client = APIClient()
    # Non-authenticated user cannot access mastery schemas
    resp = client.get(f'/api/mastery-schemas/')
    assert resp.status_code == 403
    resp = client.get(f'/api/mastery-schemas/{mastery_schema.id}/')
    assert resp.status_code == 403


@pytest.mark.django_db
def test_superadmin_mastery_schema_access(superadmin, mastery_schema, mastery_schema_other_school):
    client = APIClient()
    client.force_authenticate(user=superadmin)

    # Can list all mastery schemas
    resp = client.get('/api/mastery-schemas/')
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    expected_ids = {mastery_schema.id, mastery_schema_other_school.id}
    assert expected_ids.issubset({role['id'] for role in data})

    # Retrieving mastery schemas by ID
    resp = client.get(f'/api/mastery-schemas/{mastery_schema.id}/')
    assert resp.status_code == 200


@pytest.mark.django_db
def test_user_mastery_schema_access(
        teacher, student, mastery_schema, mastery_schema_other_school, teaching_group_with_members):
    client = APIClient()
    for user in [teacher, student]:
        client.force_authenticate(user=user)
        # Can list all mastery schemas at own school
        resp = client.get('/api/mastery-schemas/')
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        expected_ids = {mastery_schema.id}
        assert expected_ids.issubset({role['id'] for role in data})
        assert mastery_schema_other_school.id not in {role['id'] for role in data}
        # Retrieving mastery schemas by ID
        resp = client.get(f'/api/mastery-schemas/{mastery_schema.id}/')
        assert resp.status_code == 200
        resp = client.get(f'/api/mastery-schemas/{mastery_schema_other_school.id}/')
        assert resp.status_code == 404
