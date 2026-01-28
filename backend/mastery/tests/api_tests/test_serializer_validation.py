import pytest
from rest_framework.test import APIClient
from mastery.models import Observation


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
