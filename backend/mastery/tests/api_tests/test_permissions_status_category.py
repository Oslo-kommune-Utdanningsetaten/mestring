import pytest
from datetime import timedelta
from django.utils import timezone
from rest_framework.test import APIClient

thirty_days_ago = timezone.now() - timedelta(days=30)
two_days_ago = timezone.now() - timedelta(days=2)


@pytest.mark.django_db
def test_non_user_status_category_access(status_category_at_school):
    """Non-authenticated users cannot access status categories."""
    client = APIClient()

    resp = client.get("/api/status-categories/")
    assert resp.status_code == 403
    resp = client.get(f"/api/status-categories/{status_category_at_school.id}/")
    assert resp.status_code == 403


@pytest.mark.django_db
def test_superadmin_status_category_access(
        superadmin, school, other_school, mastery_schema,
        status_category_at_school, status_category_at_other_school):
    """Superadmin has full access to all status categories."""
    client = APIClient()
    client.force_authenticate(user=superadmin)

    # Endpoint requires school parameter
    resp = client.get("/api/status-categories/")
    assert resp.status_code == 400

    # Can list status categories at any school
    resp = client.get("/api/status-categories/", {"school": school.id})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == status_category_at_school.id

    resp = client.get("/api/status-categories/", {"school": other_school.id})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == status_category_at_other_school.id

    # Can retrieve status categories at any school
    resp = client.get(f"/api/status-categories/{status_category_at_school.id}/")
    assert resp.status_code == 200
    resp = client.get(f"/api/status-categories/{status_category_at_other_school.id}/")
    assert resp.status_code == 200

    # Can create status categories at any school
    resp = client.post("/api/status-categories/", {
        "title": "Standpunkt",
        "name": "standpunkt",
        "school_id": school.id,
        "mastery_schema_id": mastery_schema.id,
        "begin_at": thirty_days_ago,
        "end_at": two_days_ago,
    }, format='json')
    assert resp.status_code == 201
    created_id = resp.json()["id"]

    # Can update any status category
    resp = client.patch(f"/api/status-categories/{created_id}/", {
        "title": "Standpunkt oppdatert",
    }, format='json')
    assert resp.status_code == 200

    # Can delete any status category
    resp = client.delete(f"/api/status-categories/{created_id}/")
    assert resp.status_code == 204


@pytest.mark.django_db
def test_authenticated_status_category_access(
        school, other_school,
        school_inspector, teacher, student,
        teaching_group_with_members,
        status_category_at_school, status_category_at_other_school):
    """
    Authenticated users (students, teachers, inspectors) can list and retrieve
    status categories at schools they belong to, but not at other schools.
    They cannot create, update, or delete status categories.
    """
    client = APIClient()

    for user in [school_inspector, teacher, student]:
        client.force_authenticate(user=user)

        # Endpoint requires school parameter
        resp = client.get("/api/status-categories/")
        assert resp.status_code == 400

        # Can list status categories at their school
        resp = client.get("/api/status-categories/", {"school": school.id})
        assert resp.status_code == 200
        ids = {item["id"] for item in resp.json()}
        assert status_category_at_school.id in ids

        # Can retrieve a status category at their school
        resp = client.get(f"/api/status-categories/{status_category_at_school.id}/")
        assert resp.status_code == 200

        # Cannot list status categories at other schools (returns empty list due to scope)
        resp = client.get("/api/status-categories/", {"school": other_school.id})
        assert resp.status_code == 200
        assert resp.json() == []

        # Cannot retrieve status categories at other schools
        resp = client.get(f"/api/status-categories/{status_category_at_other_school.id}/")
        assert resp.status_code == 404

        # Cannot create status categories
        resp = client.post("/api/status-categories/", {
            "title": "Halvårsvurdering",
            "name": "halvtår-ny",
            "school_id": school.id,
            "begin_at": thirty_days_ago,
            "end_at": two_days_ago,
        }, format='json')
        assert resp.status_code == 403

        # Cannot update status categories
        resp = client.patch(
            f"/api/status-categories/{status_category_at_school.id}/",
            {"title": "Endret tittel"},
            format='json',
        )
        assert resp.status_code == 403

        # Cannot delete status categories
        resp = client.delete(f"/api/status-categories/{status_category_at_school.id}/")
        assert resp.status_code == 403


@pytest.mark.django_db
def test_school_admin_status_category_access(
        school, other_school,
        school_admin,
        mastery_schema,
        status_category_at_school, status_category_at_other_school):
    """
    School admins have full CRUD on status categories belonging to their school.
    They cannot access or modify status categories at other schools.
    """
    client = APIClient()
    client.force_authenticate(user=school_admin)

    # Endpoint requires school parameter
    resp = client.get("/api/status-categories/")
    assert resp.status_code == 400

    # Can list status categories at their school
    resp = client.get("/api/status-categories/", {"school": school.id})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == status_category_at_school.id

    # Cannot list status categories at other schools (empty list due to scope)
    resp = client.get("/api/status-categories/", {"school": other_school.id})
    assert resp.status_code == 200
    assert resp.json() == []

    # Can retrieve status categories at their school
    resp = client.get(f"/api/status-categories/{status_category_at_school.id}/")
    assert resp.status_code == 200

    # Cannot retrieve status categories at other schools
    resp = client.get(f"/api/status-categories/{status_category_at_other_school.id}/")
    assert resp.status_code == 404

    # Can create a status category at their school
    resp = client.post("/api/status-categories/", {
        "title": "Standpunkt",
        "name": "standpunkt",
        "school_id": school.id,
        "mastery_schema_id": mastery_schema.id,
        "begin_at": thirty_days_ago,
        "end_at": two_days_ago,
    }, format='json')
    assert resp.status_code == 201
    created_id = resp.json()["id"]

    # Can retrieve the newly created status category
    resp = client.get(f"/api/status-categories/{created_id}/")
    assert resp.status_code == 200

    # Can update a status category at their school
    resp = client.patch(f"/api/status-categories/{created_id}/", {
        "title": "Standpunkt oppdatert",
    }, format='json')
    assert resp.status_code == 200

    # Can delete a status category at their school
    resp = client.delete(f"/api/status-categories/{created_id}/")
    assert resp.status_code == 204

    # Cannot create a status category at another school
    resp = client.post("/api/status-categories/", {
        "title": "Halvtårsvurdering",
        "name": "halvtår-ny",
        "school_id": other_school.id,
        "begin_at": thirty_days_ago,
        "end_at": two_days_ago,
    }, format='json')
    assert resp.status_code == 403

    # Cannot update a status category at another school
    resp = client.patch(
        f"/api/status-categories/{status_category_at_other_school.id}/",
        {"title": "Hacked"},
        format='json',
    )
    assert resp.status_code == 403

    # Cannot delete a status category at another school
    resp = client.delete(f"/api/status-categories/{status_category_at_other_school.id}/")
    assert resp.status_code == 403
