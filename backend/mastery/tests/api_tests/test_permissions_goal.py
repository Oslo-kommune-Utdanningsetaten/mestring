import pytest
from rest_framework.test import APIClient
from mastery.models import User, Goal


@pytest.mark.django_db
def test_non_user_goal_access(goal_with_group):
    client = APIClient()
    # Non-authenticated user can't access goals
    resp = client.get(f'/api/goals/')
    assert resp.status_code == 403
    resp = client.get(f'/api/goals/{goal_with_group.id}/')
    assert resp.status_code == 403


@pytest.mark.django_db
def test_superadmin_goal_access(superadmin, goal_with_group, goal_personal_other_student):
    client = APIClient()
    client.force_authenticate(user=superadmin)

    # Even superadmin needs at least one of subject, group, user (params) to list all goals
    resp = client.get(f'/api/goals/')
    assert resp.status_code == 400

    # Superadmin can list goals by group
    resp = client.get(f'/api/goals/', {'group': goal_with_group.group.id})
    assert resp.status_code == 200
    data = resp.json()
    expected_ids = {goal_with_group.id}
    received_ids = {goal['id'] for goal in data}
    assert len(received_ids) == len(expected_ids)
    assert expected_ids.issubset(received_ids)

    # Superadmin can list goals by user
    resp = client.get(
        f'/api/goals/', {'student': goal_with_group.group.get_students().first().id})
    assert resp.status_code == 200
    data = resp.json()
    received_ids = {goal['id'] for goal in data}
    expected_ids = {goal_with_group.id}
    assert len(received_ids) == len(expected_ids)
    assert expected_ids.issubset(received_ids)

    # Superadmin can list personal goals by subject
    resp = client.get(f'/api/goals/', {'subject': goal_personal_other_student.subject.id})
    assert resp.status_code == 200
    data = resp.json()
    received_ids = {goal['id'] for goal in data}
    expected_ids = {goal_personal_other_student.id}
    assert len(received_ids) == len(expected_ids)
    assert expected_ids.issubset(received_ids)

    # Surperadmin can retrieve a specific goal
    resp = client.get(f'/api/goals/{goal_with_group.id}/')
    assert resp.status_code == 200
    resp = client.get(f'/api/goals/{goal_personal_other_student.id}/')
    assert resp.status_code == 200


@pytest.mark.django_db
def test_student_goal_access(
    other_teaching_group_with_members,
    goal_with_group,
    subject_without_group,
    student,
    other_student,
):
    client = APIClient()
    client.force_authenticate(user=student)

    # Personal goal owned by student
    personal_goal_self = Goal.objects.create(
        title="My personal goal",
        student=student,
        subject=subject_without_group,
    )

    # Personal goal owned by another student
    personal_goal_other = Goal.objects.create(
        title="Other student personal goal",
        student=other_student,
        subject=subject_without_group,
    )

    # Group goal in another group the student is NOT a member of
    group_goal_other = Goal.objects.create(
        title="Foreign group goal",
        group=other_teaching_group_with_members,
    )

    # Student can't list goals without required params
    resp = client.get('/api/goals/')
    assert resp.status_code == 400

    # Student can list personal and group goals
    # Should not include: personal_goal_other, group_goal_other
    resp = client.get('/api/goals/', {'student': student.id})
    assert resp.status_code == 200
    received_ids = {group['id'] for group in resp.json()}
    assert personal_goal_self.id in received_ids
    assert goal_with_group.id in received_ids
    assert personal_goal_other.id not in received_ids
    assert group_goal_other.id not in received_ids

    # Student can list group goals by own group
    resp = client.get('/api/goals/', {'group': goal_with_group.group.id})
    assert resp.status_code == 200
    data = resp.json()
    received_ids = {group['id'] for group in data}
    assert len(received_ids) == 1
    assert goal_with_group.id in received_ids

    # Studen cannot list by other group (out of scope)
    resp = client.get(
        '/api/goals/', {'group': other_teaching_group_with_members.id})
    assert resp.status_code == 200
    assert resp.json() == []

    # Student can list personal goal by subject
    resp = client.get('/api/goals/', {'subject': subject_without_group.id})
    assert resp.status_code == 200
    received_ids = {group['id'] for group in resp.json()}
    assert personal_goal_self.id in received_ids
    # Should not include other students goals nor group goals
    assert personal_goal_other.id not in received_ids
    assert goal_with_group.id not in received_ids

    # Student can retrieve own personal goal
    resp = client.get(f'/api/goals/{personal_goal_self.id}/')
    assert resp.status_code == 200

    # Student can retrieve group goal in own group
    resp = client.get(f'/api/goals/{goal_with_group.id}/')
    assert resp.status_code == 200

    # Student cannot retrieve other student's personal goal
    resp = client.get(f'/api/goals/{personal_goal_other.id}/')
    assert resp.status_code == 404

    # Student cannot retrieve foreign group goal -> 404
    resp = client.get(f'/api/goals/{group_goal_other.id}/')
    assert resp.status_code == 404

    # Student can CREATE personal goal for themselves
    resp = client.post('/api/goals/', {
        'student_id': student.id,
        'title': 'My new personal goal',
        'subject_id': subject_without_group.id
    })
    assert resp.status_code == 201
    created_goal_id = resp.json()['id']

    # Student cannot create personal goal for other students
    resp = client.post('/api/goals/', {
        'student_id': other_student.id,
        'title': 'Goal for other student',
        'subject_id': subject_without_group.id
    })
    assert resp.status_code == 403

    # Student cannot create group goal
    resp = client.post('/api/goals/', {
        'group_id': goal_with_group.group.id,
        'title': 'Group goal attempt'
    })
    assert resp.status_code == 403

    # Student can update their own personal goal
    resp = client.put(f'/api/goals/{created_goal_id}/', {
        'student_id': student.id,
        'title': 'Updated personal goal',
        'subject_id': subject_without_group.id
    })
    assert resp.status_code == 200

    # Student cannot update other student's personal goal
    resp = client.put(f'/api/goals/{personal_goal_other.id}/', {
        'student_id': other_student.id,
        'title': "Can't update this",
        'subject_id': subject_without_group.id
    })
    assert resp.status_code == 403

    # Student cannot update group goal
    resp = client.put(f'/api/goals/{goal_with_group.id}/', {
        'group_id': goal_with_group.group.id,
        'title': "Can't update group goal"
    })
    assert resp.status_code == 403

    # Stduent can delete their own personal goal
    resp = client.delete(f'/api/goals/{created_goal_id}/')
    assert resp.status_code == 204

    # Student cannot delete other student's personal goal
    resp = client.delete(f'/api/goals/{personal_goal_other.id}/')
    assert resp.status_code == 403

    # Student cannot delete group goal
    resp = client.delete(f'/api/goals/{goal_with_group.id}/')
    assert resp.status_code == 403


@pytest.mark.django_db
def test_teacher_goal_access(
    teaching_group_with_members,
    other_teaching_group_with_members,
    goal_with_group,
    subject_without_group,
    teacher,
    student,
    student_role,
    teacher_role,
    other_student,
    basis_group,
):
    """
    Tests teacher access in two phases:
    PART 1: Teaching group teacher (limited access to group goals only)
    PART 2: Same teacher becomes basis group teacher (full access to personal goals too)
    """
    client = APIClient()
    client.force_authenticate(user=teacher)

    # === PART 1: Teaching group teacher ===

    # Personal goal for student (teacher not in basis group yet)
    personal_goal = Goal.objects.create(
        title="Student's personal goal",
        student=student,
        subject=subject_without_group,
    )

    # Personal goal for a student NOT in any group taught by teacher
    personal_goal_other = Goal.objects.create(
        title="Other student personal goal",
        student=other_student,
        subject=subject_without_group,
    )

    # Group goal in a group teacher does NOT teach
    group_goal_other = Goal.objects.create(
        title="Foreign group goal",
        group=other_teaching_group_with_members,
    )

    # Teacher-created goal for an unrelated new student (should be visible because created_by)
    unrelated_student = User.objects.create(
        name="Unrelated Student",
        feide_id="unrelated-student@example.com",
        email="unrelated-student@example.com",
    )
    created_personal_goal = Goal.objects.create(
        title="Teacher created external goal",
        student=unrelated_student,
        subject=subject_without_group,
        created_by=teacher,
    )

    # Endpoint is unusable without required params
    resp = client.get('/api/goals/')
    assert resp.status_code == 400

    # Endpoint is unusable with both group and subject params
    resp = client.get(
        '/api/goals/', {'group': teaching_group_with_members.id, 'subject': subject_without_group.id})
    assert resp.status_code == 400

    # Can list goals in groups they teach
    resp = client.get('/api/goals/', {'group': teaching_group_with_members.id})
    assert resp.status_code == 200
    received_ids = {group['id'] for group in resp.json()}
    assert goal_with_group.id in received_ids
    assert group_goal_other.id not in received_ids 
    assert personal_goal.id not in received_ids

    # Teacher can't list goals for groups they don't teach => empty
    resp = client.get(
        '/api/goals/', {'group': other_teaching_group_with_members.id})
    assert resp.status_code == 200
    assert resp.json() == []

    # Teacher can list goals for students they teach
    resp = client.get('/api/goals/', {'student': student.id})
    assert resp.status_code == 200
    received_ids = {goal['id'] for goal in resp.json()}
    assert goal_with_group.id in received_ids  # Can see group goal
    assert personal_goal.id not in received_ids  # Can't see personal goal yet
    assert personal_goal_other.id not in received_ids
    assert group_goal_other.id not in received_ids

    # Teacher cannot list goals of unaffiliated students
    resp = client.get('/api/goals/', {'student': other_student.id})
    assert resp.status_code == 200
    assert resp.json() == []

    # Teacher can list an otherwise non-related personal goal, if they created it
    resp = client.get('/api/goals/', {'subject': subject_without_group.id})
    assert resp.status_code == 200
    received_ids = {group['id'] for group in resp.json()}
    assert created_personal_goal.id in received_ids
    assert personal_goal_other.id not in received_ids
    assert goal_with_group.id not in received_ids

    # Teacher can retrieve group goals they teach
    resp = client.get(f'/api/goals/{goal_with_group.id}/')
    assert resp.status_code == 200

    # Teacher cannot retrieve personal goals yet
    resp = client.get(f'/api/goals/{personal_goal.id}/')
    assert resp.status_code == 404

    # Teacher can retrieve goals they created
    resp = client.get(f'/api/goals/{created_personal_goal.id}/')
    assert resp.status_code == 200

    # Teacher cannot retrieve goals in groups they don't teach
    resp = client.get(f'/api/goals/{group_goal_other.id}/')
    assert resp.status_code == 404

    # Teacher cannot retrieve other student's personal goals
    resp = client.get(f'/api/goals/{personal_goal_other.id}/')
    assert resp.status_code == 404

    # Teacher can create goals in groups they teach
    resp = client.post('/api/goals/', {
        'group_id': teaching_group_with_members.id,
        'title': 'New group goal by teaching teacher'
    })
    assert resp.status_code == 201
    created_group_goal_id = resp.json()['id']

    # Teacher cannot create personal goals yet
    resp = client.post('/api/goals/', {
        'student_id': student.id,
        'title': 'Personal goal attempt',
        'subject_id': subject_without_group.id
    })
    assert resp.status_code == 403

    # Teacher can update group goals they teach
    resp = client.put(f'/api/goals/{goal_with_group.id}/', {
        'group_id': teaching_group_with_members.id,
        'title': 'Updated group goal'
    })
    assert resp.status_code == 200

    # Teacher cannot update personal goals yet
    resp = client.put(f'/api/goals/{personal_goal.id}/', {
        'student_id': student.id,
        'title': 'Updated personal goal attempt',
        'subject_id': subject_without_group.id
    })
    assert resp.status_code == 403

    # Teacher can delete group goals they created
    resp = client.delete(f'/api/goals/{created_group_goal_id}/')
    assert resp.status_code == 204

    # Teacher cannot delete personal goals yet
    resp = client.delete(f'/api/goals/{personal_goal.id}/')
    assert resp.status_code == 403

    # === PART 2: Same teacher becomes basis group teacher (full access) ===

    # Teacher cannot see goals in groups they don't teach yet
    other_teaching_group_with_members.add_member(student, student_role)
    goal_in_other_group = Goal.objects.create(
        title="Goal in other teaching group",
        group=other_teaching_group_with_members
    )
    resp = client.get(f'/api/goals/{goal_in_other_group.id}/')
    assert resp.status_code == 404

    # Now can see it after becoming basis teacher
    basis_group.add_member(student, student_role)
    basis_group.add_member(teacher, teacher_role)
    resp = client.get(f'/api/goals/{goal_in_other_group.id}/')
    assert resp.status_code == 200

    # But cannot modify goals in groups they don't teach
    resp = client.put(f'/api/goals/{goal_in_other_group.id}/', {
        'group_id': other_teaching_group_with_members.id,
        'title': "Can't update this"
    })
    assert resp.status_code == 403

    # Can now CRUD personal goals for their students
    resp = client.post('/api/goals/', {
        'student_id': student.id,
        'title': 'Personal goal by basis teacher',
        'subject_id': subject_without_group.id
    })
    assert resp.status_code == 201
    created_personal_goal_id = resp.json()['id']

    resp = client.put(f'/api/goals/{created_personal_goal_id}/', {
        'student_id': student.id,
        'title': 'Updated personal goal',
        'subject_id': subject_without_group.id
    })
    assert resp.status_code == 200

    resp = client.delete(f'/api/goals/{created_personal_goal_id}/')
    assert resp.status_code == 204
