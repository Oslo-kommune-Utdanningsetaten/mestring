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
        assert resp.status_code == 404

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
def test_teaching_group_teacher_observation_access(
        teacher, student, student_role, observation_on_group_goal,
        other_teaching_group_with_members, subject_with_group, subject_without_group):
    client = APIClient()
    client.force_authenticate(user=teacher)

    # Create personal goal in subject teacher teaches
    personal_goal_in_taught_subject = Goal.objects.create(
        title="Personal goal in taught subject",
        student=student,
        subject=subject_with_group,
    )
    observation_taught_subject = Observation.objects.create(
        student=student,
        goal=personal_goal_in_taught_subject,
        is_visible_to_student=True
    )

    # Create personal goal in subject teacher does not teach
    personal_goal_untaught_subject = Goal.objects.create(
        title="Personal goal in social subject",
        student=student,
        subject=subject_without_group,
    )
    observation_untaught_subject = Observation.objects.create(
        student=student,
        goal=personal_goal_untaught_subject,
        is_visible_to_student=True
    )

    # Teacher can list observations for students in groups they teach
    resp = client.get("/api/observations/", {"student": observation_on_group_goal.student.id})
    assert resp.status_code == 200
    data = resp.json()
    received_ids = {obs["id"] for obs in data}
    assert observation_on_group_goal.id in received_ids  # Group goal
    assert observation_taught_subject.id in received_ids  # Personal goal in subject they teach
    assert observation_untaught_subject.id not in received_ids  # Personal goal in subject they don't teach

    # Teacher can retrieve group goal observations
    resp = client.get(f"/api/observations/{observation_on_group_goal.id}/")
    assert resp.status_code == 200

    # Teacher can retrieve observations on personal goals in subjects they teach
    resp = client.get(f"/api/observations/{observation_taught_subject.id}/")
    assert resp.status_code == 200

    # Teacher cannot retrieve observations on personal goals in subjects they don't teach
    resp = client.get(f"/api/observations/{observation_untaught_subject.id}/")
    assert resp.status_code == 404

    # Teacher can retrieve if they're the observer
    observation_untaught_subject.observer = teacher
    observation_untaught_subject.save()
    resp = client.get(f"/api/observations/{observation_untaught_subject.id}/")
    assert resp.status_code == 200

    # Teacher can create observations on group goals they teach
    resp = client.post("/api/observations/", {
        "student_id": student.id,
        "goal_id": observation_on_group_goal.goal.id,
        "is_visible_to_student": True,
    })
    assert resp.status_code == 201
    created_group_obs_id = resp.json()["id"]

    # Teacher can update observations on group goals they teach
    resp = client.put(f"/api/observations/{observation_on_group_goal.id}/", {
        "student_id": observation_on_group_goal.student.id,
        "goal_id": observation_on_group_goal.goal.id,
        "is_visible_to_student": False,
    })
    assert resp.status_code == 200

    # Teacher can delete observations on group goals tehy teach
    resp = client.delete(f"/api/observations/{created_group_obs_id}/")
    assert resp.status_code == 204

    # Teacher cannot create/update/delete observations on group goals in groups they don't teach
    other_teaching_group_with_members.add_member(student, student_role)
    goal_other_group = Goal.objects.create(
        title="Group goal in other teaching group",
        group=other_teaching_group_with_members,
    )
    observation_other_group = Observation.objects.create(
        student=student,
        goal=goal_other_group,
        is_visible_to_student=True
    )

    # Teacher cannot retrieve observation in group they don't teach
    resp = client.get(f"/api/observations/{observation_other_group.id}/")
    assert resp.status_code == 404

    # Teacher cannot create observation in group they don't teach
    resp = client.post("/api/observations/", {
        "student_id": student.id,
        "goal_id": goal_other_group.id,
        "is_visible_to_student": True,
    })
    assert resp.status_code == 403

    # Teacher cannot update observation in group they don't teach
    resp = client.put(f"/api/observations/{observation_other_group.id}/", {
        "student_id": student.id,
        "goal_id": goal_other_group.id,
        "is_visible_to_student": False,
    })
    assert resp.status_code == 403

    # Teacher cannot delete observation in group they don't teach
    resp = client.delete(f"/api/observations/{observation_other_group.id}/")
    assert resp.status_code == 403

    # Teacher can create observations on personal goals in subjects they teach
    resp = client.post("/api/observations/", {
        "student_id": student.id,
        "goal_id": personal_goal_in_taught_subject.id,
        "is_visible_to_student": True,
    })
    assert resp.status_code == 201
    created_taught_subject_obs_id = resp.json()["id"]

    # Teacher cannot create observations on personal goals in subjects they don't teach
    resp = client.post("/api/observations/", {
        "student_id": student.id,
        "goal_id": personal_goal_untaught_subject.id,
        "is_visible_to_student": True,
    })
    assert resp.status_code == 403

    # Teacher can update observations on personal goals in subjects they teach
    resp = client.put(f"/api/observations/{created_taught_subject_obs_id}/", {
        "student_id": student.id,
        "goal_id": personal_goal_in_taught_subject.id,
        "is_visible_to_student": False,
    })
    assert resp.status_code == 200

    # Teacher cannot update observations on personal goals in subjects they don't teach
    resp = client.put(f"/api/observations/{observation_untaught_subject.id}/", {
        "student_id": student.id,
        "goal_id": personal_goal_untaught_subject.id,
        "is_visible_to_student": False,
    })
    assert resp.status_code == 403

    # Teacher can delete observations on personal goals in subjects they teach
    resp = client.delete(f"/api/observations/{created_taught_subject_obs_id}/")
    assert resp.status_code == 204

    # Teacher cannot delete observations on personal goals in subjects they don't teach
    resp = client.delete(f"/api/observations/{observation_untaught_subject.id}/")
    assert resp.status_code == 403

    # Teacher can see invisible observations in groups they teach
    observation_on_group_goal.is_visible_to_student = False
    observation_on_group_goal.save()
    resp = client.get(f"/api/observations/{observation_on_group_goal.id}/")
    assert resp.status_code == 200


@pytest.mark.django_db
def test_basis_group_teacher_observation_access(
        teacher, other_teacher, student, student_role, teacher_role, observation_on_personal_goal,
        basis_group, other_teaching_group_with_members):
    """
    Test that basis group teachers have full access to observations for students in their basis group.
    """
    client = APIClient()
    client.force_authenticate(user=teacher)

    # Create observation in group they don't teach
    other_teaching_group_with_members.add_member(student, student_role)
    goal = Goal.objects.create(
        title="Lese 2 bøker",
        group=other_teaching_group_with_members
    )
    observation = Observation.objects.create(student=student, goal=goal, is_visible_to_student=True)

    # Teacher cannot see it yet (not their group, not basis teacher yet)
    resp = client.get(f"/api/observations/{observation.id}/")
    assert resp.status_code == 404

    # Make teacher a basis group teacher
    basis_group.add_member(student, student_role)
    basis_group.add_member(teacher, teacher_role)

    # Now basis teacher can see observations in groups they don't teach
    resp = client.get(f"/api/observations/{observation.id}/")
    assert resp.status_code == 200

    # But cannot modify observations in groups they don't teach
    resp = client.put(f"/api/observations/{observation.id}/", {
        "student_id": observation.student.id,
        "goal_id": observation.goal.id,
        "is_visible_to_student": True,
    })
    assert resp.status_code == 403

    # Teacher can access invisible observations for their students
    observation.is_visible_to_student = False
    observation.save()
    resp = client.get(f"/api/observations/{observation.id}/")
    assert resp.status_code == 200

    # Basis teacher can CRUD observations on personal goals for their students
    resp = client.post("/api/observations/", {
        "student_id": student.id,
        "goal_id": observation_on_personal_goal.goal.id,
        "is_visible_to_student": True,
    })
    assert resp.status_code == 201
    created_personal_obs_id = resp.json()["id"]

    resp = client.put(f"/api/observations/{created_personal_obs_id}/", {
        "student_id": student.id,
        "goal_id": observation_on_personal_goal.goal.id,
        "is_visible_to_student": False,
    })
    assert resp.status_code == 200

    resp = client.delete(f"/api/observations/{created_personal_obs_id}/")
    assert resp.status_code == 204

    # Teacher cannot modify observations created by other teachers
    observation_by_other_teacher = Observation.objects.create(
        student=student,
        goal=observation_on_personal_goal.goal,
        is_visible_to_student=True,
        created_by=other_teacher
    )

    # Teacher can retrieve it in their scope as basis teacher
    resp = client.get(f"/api/observations/{observation_by_other_teacher.id}/")
    assert resp.status_code == 200

    # But cannot update it
    resp = client.put(f"/api/observations/{observation_by_other_teacher.id}/", {
        "student_id": student.id,
        "goal_id": observation_on_personal_goal.goal.id,
        "is_visible_to_student": False,
    })
    assert resp.status_code == 403

    # And cannot delete it
    resp = client.delete(f"/api/observations/{observation_by_other_teacher.id}/")
    assert resp.status_code == 403


@pytest.mark.django_db
def test_student_observation_access(
        student, observation_on_personal_goal, observation_on_group_goal, other_student,
        observation_on_personal_goal_other_student):
    client = APIClient()
    client.force_authenticate(user=student)

    # Students can access observations they are the target of that are visible
    resp = client.get(f"/api/observations/{observation_on_group_goal.id}/")
    assert resp.status_code == 200
    resp = client.get(f"/api/observations/{observation_on_personal_goal.id}/")
    assert resp.status_code == 200

    # Students cannot access observations that are not visible to them
    observation_on_group_goal.is_visible_to_student = False
    observation_on_group_goal.save()
    resp = client.get(f"/api/observations/{observation_on_group_goal.id}/")
    assert resp.status_code == 404

    # Student cannot access observations about other students
    resp = client.get(f"/api/observations/{observation_on_personal_goal_other_student.id}/")
    assert resp.status_code == 404

    # Can CREATE observation about themselves
    resp = client.post("/api/observations/", {
        "student_id": student.id,
        "goal_id": observation_on_personal_goal.goal.id,
        "is_visible_to_student": True,
        "created_by_id": student.id,
    })
    assert resp.status_code == 201
    created_obs_id = resp.json()["id"]

    # Student cannot create observation and set is_visible_to_student to False it forces to True
    resp = client.post("/api/observations/", {
        "student_id": student.id,
        "goal_id": observation_on_personal_goal.goal.id,
        "is_visible_to_student": False,
        "created_by_id": student.id,
    })
    assert resp.status_code == 201
    created_invisible_attempt_id = resp.json()["id"]
    forced_visible_observation = Observation.objects.get(id=created_invisible_attempt_id)
    assert forced_visible_observation.is_visible_to_student is True  # Enforced to True

    # Cannot CREATE observation about other students
    resp = client.post("/api/observations/", {
        "student_id": other_student.id,
        "goal_id": observation_on_personal_goal.goal.id,
        "is_visible_to_student": True,
        "created_by_id": student.id,
    })
    assert resp.status_code == 403

    # Can UPDATE observation they created about themselves
    resp = client.put(f"/api/observations/{created_obs_id}/", {
        "student_id": student.id,
        "goal_id": observation_on_personal_goal.goal.id,
        "is_visible_to_student": True,
        "mastery_value": 41,
        "mastery_description": "Good job, keep up the good work",
        "feedforward": "You can do it"
    })
    assert resp.status_code == 200
    updated_obs = Observation.objects.get(id=created_obs_id)
    assert updated_obs.mastery_value == 41
    assert updated_obs.mastery_description == "Good job, keep up the good work"
    assert updated_obs.feedforward == "You can do it"

    # Cannot UPDATE observation they didn't create
    resp = client.put(f"/api/observations/{observation_on_group_goal.id}/", {
        "student_id": observation_on_group_goal.student.id,
        "goal_id": observation_on_group_goal.goal.id,
        "is_visible_to_student": False,
        "mastery_value": 72,
        "mastery_description": "Trying to cheat the system it don't work",
        "feedforward": "You can't do it",
    })
    assert resp.status_code == 403

    # Can DELETE observation they created about themselves
    resp = client.delete(f"/api/observations/{created_obs_id}/")
    assert resp.status_code == 204

    # Cannot DELETE observation they didn't create
    resp = client.delete(f"/api/observations/{observation_on_group_goal.id}/")
    assert resp.status_code == 403
