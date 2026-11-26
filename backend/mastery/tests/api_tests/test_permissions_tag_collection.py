import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_non_user_tag_collection_access(tag_collection_at_school):
    """Non-authenticated users cannot access tag collections."""
    client = APIClient()

    resp = client.get("/api/tag-collections/")
    assert resp.status_code == 403
    resp = client.get(f"/api/tag-collections/{tag_collection_at_school.id}/")
    assert resp.status_code == 403


@pytest.mark.django_db
def test_superadmin_tag_collection_access(
        superadmin, school, other_school, subject_with_group,
        tag_collection_at_school, tag_collection_at_other_school):
    """Superadmin has full access to all tag collections."""
    client = APIClient()
    client.force_authenticate(user=superadmin)

    # Can list tag collections at any school
    resp = client.get("/api/tag-collections/", {"school": other_school.id})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == tag_collection_at_other_school.id

    # Can retrieve tag collections at any school
    resp = client.get(f"/api/tag-collections/{tag_collection_at_other_school.id}/")
    assert resp.status_code == 200

    # Can create tag collections at any school
    resp = client.post("/api/tag-collections/", {
        "school_id": school.id,
        "subject_id": subject_with_group.id,
        "tags": ["Prøve"],
    }, format='json')
    assert resp.status_code == 201
    created_id = resp.json()["id"]

    # Can update any tag collection
    resp = client.patch(f"/api/tag-collections/{created_id}/", {
        "tags": ["Prøve", "Innlevering"],
    }, format='json')
    assert resp.status_code == 200

    # Can delete any tag collection
    resp = client.delete(f"/api/tag-collections/{created_id}/")
    assert resp.status_code == 204


@pytest.mark.django_db
def test_user_tag_collection_read_access(
        school, other_school, teacher, student, school_admin,
        teaching_group_with_members, tag_collection_at_school, tag_collection_at_other_school):
    """
    Users can list and retrieve tag collections at their own school, but not at other schools.
    Students cannot create, update or delete tag collections.
    """
    client = APIClient()

    for user in [teacher, student, school_admin]:
        client.force_authenticate(user=user)

        # Can list tag collections at their school
        resp = client.get("/api/tag-collections/", {"school": school.id})
        assert resp.status_code == 200
        ids = {item["id"] for item in resp.json()}
        assert ids == {tag_collection_at_school.id}

        # Cannot list tag collections at other schools (returns empty list due to scope)
        resp = client.get("/api/tag-collections/", {"school": other_school.id})
        assert resp.status_code == 200
        assert resp.json() == []

        # Can retrieve a tag collection at their school
        resp = client.get(f"/api/tag-collections/{tag_collection_at_school.id}/")
        assert resp.status_code == 200

        # Cannot retrieve tag collections at other schools
        resp = client.get(f"/api/tag-collections/{tag_collection_at_other_school.id}/")
        assert resp.status_code == 404

    client.force_authenticate(user=student)

    # Student cannot create a tag collection
    resp = client.post("/api/tag-collections/", {
        "school_id": school.id,
        "subject_id": tag_collection_at_school.subject_id,
        "tags": ["Hacked"],
    }, format='json')
    assert resp.status_code == 403

    # Student cannot update a tag collection
    resp = client.patch(
        f"/api/tag-collections/{tag_collection_at_school.id}/",
        {"tags": ["Hacked"]},
        format='json',
    )
    assert resp.status_code == 403

    # Student cannot delete a tag collection
    resp = client.delete(f"/api/tag-collections/{tag_collection_at_school.id}/")
    assert resp.status_code == 403


@pytest.mark.django_db
def test_school_admin_or_inspector_tag_collection_access(
        school, other_school, school_admin, school_inspector,
        subject_owned_by_school, tag_collection_at_other_school):
    """
    School admins and inspectors have full CRUD on tag collections belonging to their school.
    They cannot create or modify tag collections at other schools.
    """
    client = APIClient()

    for user in [school_admin, school_inspector]:
        client.force_authenticate(user=user)

        # Can create a tag collection at their school
        resp = client.post("/api/tag-collections/", {
            "school_id": school.id,
            "subject_id": subject_owned_by_school.id,
            "tags": ["Prøve"],
        }, format='json')
        assert resp.status_code == 201
        created_id = resp.json()["id"]

        # Can update a tag collection at their school
        resp = client.patch(f"/api/tag-collections/{created_id}/", {
            "tags": ["Prøve", "Innlevering"],
        }, format='json')
        assert resp.status_code == 200

        # Can delete a tag collection at their school
        resp = client.delete(f"/api/tag-collections/{created_id}/")
        assert resp.status_code == 204

        # Cannot create a tag collection at another school
        resp = client.post("/api/tag-collections/", {
            "school_id": other_school.id,
            "subject_id": tag_collection_at_other_school.subject_id,
            "tags": ["Hacked"],
        }, format='json')
        assert resp.status_code == 403

        # Cannot update a tag collection at another school
        resp = client.patch(
            f"/api/tag-collections/{tag_collection_at_other_school.id}/",
            {"tags": ["Hacked"]},
            format='json',
        )
        assert resp.status_code == 403

        # Cannot delete a tag collection at another school
        resp = client.delete(f"/api/tag-collections/{tag_collection_at_other_school.id}/")
        assert resp.status_code == 403


@pytest.mark.django_db
def test_teacher_tag_collection_write_access(
        school, teacher, subject_with_group, subject_owned_by_school,
        tag_collection_at_school, tag_collection_at_other_school):
    """
    Teachers have full CRUD on tag collections for subjects taught in their groups.
    They cannot create or modify tag collections for other subjects or at other schools.
    """
    client = APIClient()
    client.force_authenticate(user=teacher)

    # Can create a tag collection for a subject they teach
    resp = client.post("/api/tag-collections/", {
        "school_id": school.id,
        "subject_id": subject_with_group.id,
        "tags": ["Prøve"],
    }, format='json')
    assert resp.status_code == 201
    created_id = resp.json()["id"]

    # Can update a tag collection for a subject they teach
    resp = client.patch(f"/api/tag-collections/{tag_collection_at_school.id}/", {
        "tags": ["Prøve", "Innlevering"],
    }, format='json')
    assert resp.status_code == 200

    # Can delete a tag collection for a subject they teach
    resp = client.delete(f"/api/tag-collections/{created_id}/")
    assert resp.status_code == 204

    # Cannot create a tag collection for a subject they do not teach
    resp = client.post("/api/tag-collections/", {
        "school_id": school.id,
        "subject_id": subject_owned_by_school.id,
        "tags": ["Hacked"],
    }, format='json')
    assert resp.status_code == 403

    # Cannot update a tag collection at another school
    resp = client.patch(
        f"/api/tag-collections/{tag_collection_at_other_school.id}/",
        {"tags": ["Hacked"]},
        format='json',
    )
    assert resp.status_code == 403

    # Cannot delete a tag collection at another school
    resp = client.delete(f"/api/tag-collections/{tag_collection_at_other_school.id}/")
    assert resp.status_code == 403
