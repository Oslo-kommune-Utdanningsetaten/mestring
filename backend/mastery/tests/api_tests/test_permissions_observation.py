import pytest
from rest_framework.test import APIClient
from mastery.models import Observation, Goal


@pytest.mark.django_db
def test_non_user_observation_access(observation_on_personal_goal):
    client = APIClient()
    # Non-authenticated user cannot access observations
    resp = client.get(f"/api/observations/")
    assert resp.status_code == 403
    resp = client.get(f"/api/observations/{observation_on_personal_goal.id}/")
    assert resp.status_code == 403


@pytest.mark.django_db
def test_superadmin_observation_access(
    superadmin, teacher, observation_on_personal_goal, observation_on_group_goal
):
    client = APIClient()
    client.force_authenticate(user=superadmin)

    # Need at least one parameter for valid request
    resp = client.get("/api/observations/")
    assert resp.status_code == 400

    # Can list observations by student
    resp = client.get(
        "/api/observations/", {"student": observation_on_personal_goal.student.id}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    expected_ids = {observation_on_personal_goal.id, observation_on_group_goal.id}
    assert expected_ids.issubset({role["id"] for role in data})

    # Can list observations by observer
    observation_on_group_goal.observer = teacher
    observation_on_group_goal.save()
    observation_on_personal_goal.observer = teacher
    observation_on_personal_goal.save()
    resp = client.get(
        "/api/observations/", {"observer": observation_on_personal_goal.observer.id}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    expected_ids = {observation_on_personal_goal.id, observation_on_group_goal.id}
    assert expected_ids.issubset({role["id"] for role in data})

    # Can list observations by goal
    resp = client.get(
        "/api/observations/", {"goal": observation_on_personal_goal.goal.id}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    expected_ids = {observation_on_personal_goal.id}
    assert expected_ids.issubset({role["id"] for role in data})

    # Retrieving observations by ID
    resp = client.get(f"/api/observations/{observation_on_personal_goal.id}/")
    assert resp.status_code == 200


@pytest.mark.django_db
def test_user_observation_access(
        teacher, student, other_student, observation_on_personal_goal_other_student):
    client = APIClient()
    for user in [student, teacher]:
        client.force_authenticate(user=user)

        # User cannot access observation on other student
        resp = client.get(f"/api/observations/{observation_on_personal_goal_other_student.id}/")
        assert resp.status_code == 403

        # User can retrieve observations they created
        observation_on_personal_goal_other_student.created_by = user
        observation_on_personal_goal_other_student.save()
        resp = client.get(f"/api/observations/{observation_on_personal_goal_other_student.id}/")
        assert resp.status_code == 200

        # User can retrieve observations where they are observer
        observation_on_personal_goal_other_student.created_by = other_student
        observation_on_personal_goal_other_student.observer = user
        observation_on_personal_goal_other_student.save()
        resp = client.get(f"/api/observations/{observation_on_personal_goal_other_student.id}/")
        assert resp.status_code == 200


@pytest.mark.django_db
def test_teacher_observation_access(
        teacher, student, student_role, teacher_role, observation_on_personal_goal, observation_on_group_goal,
        basis_group, other_teaching_group_with_members):
    client = APIClient()
    client.force_authenticate(user=teacher)

    # Teacher can access observations for students in their teaching group
    resp = client.get("/api/observations/", {"student": observation_on_group_goal.student.id})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    expected_ids = {observation_on_group_goal.id}
    assert expected_ids.issubset({role["id"] for role in data})

    # Teacher can retrieve observations by ID
    resp = client.get(f"/api/observations/{observation_on_group_goal.id}/")
    assert resp.status_code == 200

    # Teacher cannot access observation if they are unaffiliated with the student
    resp = client.get(f"/api/observations/{observation_on_personal_goal.id}/")
    assert resp.status_code == 403

    # Teacher can retrieve that observation if they are observer
    observation_on_personal_goal.observer = teacher
    observation_on_personal_goal.save()
    resp = client.get(f"/api/observations/{observation_on_personal_goal.id}/")
    assert resp.status_code == 200

    # Teacher cannot retrieve a students observation in from a different group
    other_teaching_group_with_members.add_member(student, student_role)
    goal = Goal.objects.create(
        title="Lese 2 bøker",
        group=other_teaching_group_with_members
    )
    observation = Observation.objects.create(student=student, goal=goal, is_visible_to_student=True)
    resp = client.get(f"/api/observations/{observation.id}/")
    assert resp.status_code == 403

    # Teacher can in fact access that same observation if student is in their basis groups
    basis_group.add_member(student, student_role)
    basis_group.add_member(teacher, teacher_role)
    resp = client.get(f"/api/observations/{observation.id}/")
    assert resp.status_code == 200

    # Teacher can access invisible observations for their students
    observation.is_visible_to_student = False
    observation.save()
    resp = client.get(f"/api/observations/{observation.id}/")
    assert resp.status_code == 200


@pytest.mark.django_db
def test_student_observation_access(student, observation_on_personal_goal, observation_on_group_goal):
    client = APIClient()
    client.force_authenticate(user=student)

    # Students can access observations they are the target of
    resp = client.get(f"/api/observations/{observation_on_group_goal.id}/")
    assert resp.status_code == 200
    resp = client.get(f"/api/observations/{observation_on_personal_goal.id}/")
    assert resp.status_code == 200

    # Students cannot access observations that are not visible to them
    observation_on_group_goal.is_visible_to_student = False
    observation_on_group_goal.save()
    resp = client.get(f"/api/observations/{observation_on_group_goal.id}/")
    assert resp.status_code == 403
    observation_on_personal_goal.is_visible_to_student = False
    observation_on_personal_goal.save()
    resp = client.get(f"/api/observations/{observation_on_personal_goal.id}/")
    assert resp.status_code == 403

    # Not visible takes precedent over created_by student
    observation_on_personal_goal.is_visible_to_student = False
    observation_on_personal_goal.created_by = student
    observation_on_personal_goal.save()
    resp = client.get(f"/api/observations/{observation_on_personal_goal.id}/")
    assert resp.status_code == 403

    # Not visible takes precedent over observer
    observation_on_personal_goal.is_visible_to_student = False
    observation_on_personal_goal.created_by = None
    observation_on_personal_goal.observer = student
    observation_on_personal_goal.save()
    resp = client.get(f"/api/observations/{observation_on_personal_goal.id}/")
    assert resp.status_code == 403
