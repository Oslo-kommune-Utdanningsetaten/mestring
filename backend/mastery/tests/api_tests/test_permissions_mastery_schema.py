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


@pytest.mark.django_db
def test_school_admin_or_inspector_mastery_schema_access(
        school, other_school, school_admin, school_inspector,
        mastery_schema, mastery_schema_other_school):
    """
    School admins and inspectors have full CRUD on mastery schemas belonging to their school.
    They cannot create or modify mastery schemas at other schools.
    """
    client = APIClient()
    for user in [school_admin, school_inspector]:
        client.force_authenticate(user=user)

        # Can create a mastery schema at their school
        resp = client.post("/api/mastery-schemas/", {
            "title": "Nytt skjema",
            "school_id": school.id,
        }, format='json')
        assert resp.status_code == 201
        created_id = resp.json()["id"]

        # Can update a mastery schema at their school
        resp = client.patch(f"/api/mastery-schemas/{created_id}/", {
            "title": "Oppdatert skjema",
        }, format='json')
        assert resp.status_code == 200

        # Can delete a mastery schema at their school
        resp = client.delete(f"/api/mastery-schemas/{created_id}/")
        assert resp.status_code == 204

        # Cannot create a mastery schema at another school
        resp = client.post("/api/mastery-schemas/", {
            "title": "Uautorisert skjema",
            "school_id": other_school.id,
        }, format='json')
        assert resp.status_code == 403

        # Cannot update a mastery schema at another school
        resp = client.patch(
            f"/api/mastery-schemas/{mastery_schema_other_school.id}/",
            {"title": "Hacked"},
            format='json',
        )
        assert resp.status_code == 403

        # Cannot delete a mastery schema at another school
        resp = client.delete(f"/api/mastery-schemas/{mastery_schema_other_school.id}/")
        assert resp.status_code == 403


@pytest.mark.django_db
def test_user_mastery_schema_write_access_denied(teacher, mastery_schema):
    """Teachers and students cannot create, update or delete mastery schemas."""
    client = APIClient()
    client.force_authenticate(user=teacher)

    # Cannot create a mastery schema
    resp = client.post("/api/mastery-schemas/", {
        "title": "Nytt skjema",
        "school_id": mastery_schema.school_id,
    }, format='json')
    assert resp.status_code == 403

    # Cannot update a mastery schema
    resp = client.patch(
        f"/api/mastery-schemas/{mastery_schema.id}/",
        {"title": "Hacked"},
        format='json',
    )
    assert resp.status_code == 403

    # Cannot delete a mastery schema
    resp = client.delete(f"/api/mastery-schemas/{mastery_schema.id}/")
    assert resp.status_code == 403
