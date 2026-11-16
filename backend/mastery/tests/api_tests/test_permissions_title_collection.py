import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_non_user_title_collection_access(title_collection_at_school):
    """Non-authenticated users cannot access title collections."""
    client = APIClient()

    resp = client.get("/api/title-collections/")
    assert resp.status_code == 403
    resp = client.get(f"/api/title-collections/{title_collection_at_school.id}/")
    assert resp.status_code == 403


@pytest.mark.django_db
def test_superadmin_title_collection_access(
        superadmin, school, other_school, title_collection_at_school, title_collection_at_other_school):
    """Superadmin has full access to all title collections."""
    client = APIClient()
    client.force_authenticate(user=superadmin)

    # Can list title collections at any school
    resp = client.get("/api/title-collections/", {"school": other_school.id})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == title_collection_at_other_school.id

    # Can retrieve title collections at any school
    resp = client.get(f"/api/title-collections/{title_collection_at_other_school.id}/")
    assert resp.status_code == 200

    # Can create title collections at any school
    resp = client.post("/api/title-collections/", {
        "school_id": school.id,
        "titles": ["Prøve"],
    }, format='json')
    assert resp.status_code == 201
    created_id = resp.json()["id"]

    # Can update any title collection
    resp = client.patch(f"/api/title-collections/{created_id}/", {
        "titles": ["Prøve", "Innlevering"],
    }, format='json')
    assert resp.status_code == 200

    # Can delete any title collection
    resp = client.delete(f"/api/title-collections/{created_id}/")
    assert resp.status_code == 204


@pytest.mark.django_db
def test_school_admin_or_inspector_title_collection_access(
        school, other_school, school_admin, school_inspector,
        title_collection_at_school, title_collection_at_other_school):
    """
    School admins and inspectors can create, update and delete title collections belonging to their school.
    They cannot create or modify title collections at other schools.
    """
    client = APIClient()

    for user in [school_admin, school_inspector]:
        client.force_authenticate(user=user)

        # Can create a title collection at their school
        resp = client.post("/api/title-collections/", {
            "school_id": school.id,
            "titles": ["Prøve"],
        }, format='json')
        assert resp.status_code == 201
        created_id = resp.json()["id"]

        # Can update a title collection at their school
        resp = client.patch(f"/api/title-collections/{created_id}/", {
            "titles": ["Prøve", "Innlevering"],
        }, format='json')
        assert resp.status_code == 200

        # Can delete a title collection at their school
        resp = client.delete(f"/api/title-collections/{created_id}/")
        assert resp.status_code == 204

        # Cannot create a title collection at another school
        resp = client.post("/api/title-collections/", {
            "school_id": other_school.id,
            "titles": ["Hacked"],
        }, format='json')
        assert resp.status_code == 403

        # Cannot update a title collection at another school
        resp = client.patch(
            f"/api/title-collections/{title_collection_at_other_school.id}/",
            {"titles": ["Hacked"]},
            format='json',
        )
        assert resp.status_code == 403

        # Cannot delete a title collection at another school
        resp = client.delete(f"/api/title-collections/{title_collection_at_other_school.id}/")
        assert resp.status_code == 403


@pytest.mark.django_db
def test_teacher_title_collection_access(
        school, teacher, teaching_group_with_members,
        title_collection_at_school, title_collection_at_other_school):
    """
    Teachers can retrieve title collections at their own school, but not at other schools.
    Teachers cannot create, update or delete title collections.
    """
    client = APIClient()
    client.force_authenticate(user=teacher)

    # Can retrieve a title collection at their school
    resp = client.get(f"/api/title-collections/{title_collection_at_school.id}/")
    assert resp.status_code == 200

    # Cannot retrieve title collections at other schools
    resp = client.get(f"/api/title-collections/{title_collection_at_other_school.id}/")
    assert resp.status_code == 404

    # Cannot create a title collection
    resp = client.post("/api/title-collections/", {
        "school_id": school.id,
        "titles": ["Hacked"],
    }, format='json')
    assert resp.status_code == 403

    # Cannot update a title collection
    resp = client.patch(
        f"/api/title-collections/{title_collection_at_school.id}/",
        {"titles": ["Hacked"]},
        format='json',
    )
    assert resp.status_code == 403

    # Cannot delete a title collection
    resp = client.delete(f"/api/title-collections/{title_collection_at_school.id}/")
    assert resp.status_code == 403


@pytest.mark.django_db
def test_student_title_collection_access(
        student, school, teaching_group_with_members, title_collection_at_school):
    """Students cannot access or modify title collections."""
    client = APIClient()
    client.force_authenticate(user=student)

    resp = client.get(f"/api/title-collections/{title_collection_at_school.id}/")
    assert resp.status_code == 404

    resp = client.post("/api/title-collections/", {
        "school_id": school.id,
        "titles": ["Hacked"],
    }, format='json')
    assert resp.status_code == 403
