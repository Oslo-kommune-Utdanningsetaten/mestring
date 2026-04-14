import pytest
from datetime import timedelta
from django.utils import timezone
from rest_framework.test import APIClient
from mastery.models import Observation, Status


@pytest.mark.django_db
def test_create_rejects_mastery_value_outside_schema_range(
    db, superadmin, student, goal_individual, mastery_schema
):
    # mastery_value outside schema range should be rejected
    client = APIClient()
    client.force_authenticate(user=superadmin)
    goal_individual.mastery_schema = mastery_schema
    goal_individual.save()
    _, max = mastery_schema.get_value_range()

    resp = client.post("/api/observations/", {
        "goal_id": goal_individual.id,
        "student_id": student.id,
        "mastery_value": max + 1,
    }, format='json')
    assert resp.status_code == 400
    assert "masteryValue" in resp.json()


@pytest.mark.django_db
def test_partial_update_rejects_mastery_value_outside_schema_range(
    db, superadmin, student, goal_individual, mastery_schema
):
    # Partial update should also validate against schema
    client = APIClient()
    client.force_authenticate(user=superadmin)
    goal_individual.mastery_schema = mastery_schema
    goal_individual.save()
    min, max = mastery_schema.get_value_range()

    resp = client.post("/api/observations/", {
        "goal_id": goal_individual.id,
        "student_id": student.id,
        "mastery_value": max,
    }, format='json')
    assert resp.status_code == 201

    resp = client.patch(f"/api/observations/{resp.json().get('id')}/", {
        "mastery_value": min - 1,
    }, format='json')
    assert resp.status_code == 400
    assert "masteryValue" in resp.json()


# --- Status ---

def _status_payload(student, subject_with_group, school):
    return {
        "student_id": student.id,
        "subject_id": subject_with_group.id,
        "school_id": school.id,
        "begin_at": (timezone.now() - timedelta(days=30)).isoformat(),
        "end_at": timezone.now().isoformat(),
    }


@pytest.mark.django_db
def test_status_create_rejects_mastery_value_outside_schema_range(
    db, superadmin, student, subject_with_group, school, mastery_schema
):
    client = APIClient()
    client.force_authenticate(user=superadmin)
    _, max = mastery_schema.get_value_range()

    payload = _status_payload(student, subject_with_group, school)
    payload["mastery_schema_id"] = mastery_schema.id
    payload["mastery_value"] = max + 1

    resp = client.post("/api/status/", payload, format='json')
    assert resp.status_code == 400
    assert "masteryValue" in resp.json()


@pytest.mark.django_db
def test_status_create_accepts_mastery_value_within_schema_range(
    db, superadmin, student, subject_with_group, school, mastery_schema
):
    client = APIClient()
    client.force_authenticate(user=superadmin)
    _, max = mastery_schema.get_value_range()

    payload = _status_payload(student, subject_with_group, school)
    payload["mastery_schema_id"] = mastery_schema.id
    payload["mastery_value"] = max

    resp = client.post("/api/status/", payload, format='json')
    assert resp.status_code == 201


@pytest.mark.django_db
def test_status_partial_update_rejects_mastery_value_outside_schema_range(
    db, superadmin, student, subject_with_group, school, mastery_schema
):
    # Partial update sending only mastery_value should still validate against existing schema
    client = APIClient()
    client.force_authenticate(user=superadmin)
    min, max = mastery_schema.get_value_range()

    payload = _status_payload(student, subject_with_group, school)
    payload["mastery_schema_id"] = mastery_schema.id
    payload["mastery_value"] = max

    resp = client.post("/api/status/", payload, format='json')
    assert resp.status_code == 201
    status_id = resp.json()["id"]

    resp = client.patch(f"/api/status/{status_id}/", {
        "mastery_value": min - 1,
    }, format='json')
    assert resp.status_code == 400
    assert "masteryValue" in resp.json()


@pytest.mark.django_db
def test_status_partial_update_allows_valid_mastery_value(
    db, superadmin, student, subject_with_group, school, mastery_schema
):
    client = APIClient()
    client.force_authenticate(user=superadmin)
    min, max = mastery_schema.get_value_range()

    payload = _status_payload(student, subject_with_group, school)
    payload["mastery_schema_id"] = mastery_schema.id
    payload["mastery_value"] = max

    resp = client.post("/api/status/", payload, format='json')
    assert resp.status_code == 201
    status_id = resp.json()["id"]

    resp = client.patch(f"/api/status/{status_id}/", {
        "mastery_value": min,
    }, format='json')
    assert resp.status_code == 200
