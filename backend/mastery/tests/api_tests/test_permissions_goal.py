import pytest
from rest_framework.test import APIClient
from mastery.models import User, Goal


@pytest.mark.django_db
def test_non_user_goal_access(goal_with_group):
    client = APIClient()
    # Non-authenticated user cannot access goals
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

    # Student cannot retrieve foreign group goal -> 403
    resp = client.get(f'/api/goals/{group_goal_other.id}/')
    assert resp.status_code == 404

    personal_goal_data = {
        'title': "My new personal goal",
        'student_id': student.id,
        'subject_id': subject_without_group.id
    }

    # Student can create a personal goal for themself
    resp = client.post('/api/goals/', personal_goal_data)
    assert resp.status_code == 201

    # Student cannot create a personal goal for another student
    other_student_goal_data = {
        'title': "Goal for another student",
        'student_id': other_student.id,
        'subject_id': subject_without_group.id
    }
    resp = client.post('/api/goals/', other_student_goal_data)
    assert resp.status_code == 403

    # student cannot create a group goal
    group_goal_data = {
        'title': "Group goal I should not create",
        'group_id': goal_with_group.group.id
    }
    resp = client.post('/api/goals/', group_goal_data)
    assert resp.status_code == 403

    # Student can update personal goal they own
    resp = client.put(f'/api/goals/{personal_goal_self.id}/', {
        'title': "Updated title"
    })
    assert resp.status_code == 200

    # Student cannot update personal goal owned by another student
    resp = client.put(f'/api/goals/{personal_goal_other.id}/', {
        'title': "Updated title for other student",
    })
    assert resp.status_code == 403

    # Student cannot update group goal even if in the group
    resp = client.put(f'/api/goals/{goal_with_group.id}/', {
        'title': "Updated title for group goal",
    })
    assert resp.status_code == 403

    # Student can delete personal goal they own
    resp = client.delete(f'/api/goals/{personal_goal_self.id}/')
    assert resp.status_code == 204

    # Student cannot delete personal goal owned by another student
    resp = client.delete(f'/api/goals/{personal_goal_other.id}/')
    assert resp.status_code == 403

    # Student cannot delete group goal even if in the group
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
    other_student,
):
    """
    Teacher visibility rules (GoalAccessPolicy.scope_queryset):
      - Goals created_by teacher
      - Group goals in groups they teach
      - Student personal goals where the student is in a group they teach
    Retrieval mirrors those (plus created_by).
    """
    client = APIClient()
    client.force_authenticate(user=teacher)

    # Personal goal for a student they teach
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

    # Teacher can list goals by group they teach
    resp = client.get('/api/goals/', {'group': teaching_group_with_members.id})
    assert resp.status_code == 200
    received_ids = {group['id'] for group in resp.json()}
    assert goal_with_group.id in received_ids
    assert group_goal_other.id not in received_ids
    assert personal_goal.id not in received_ids

    # Teacher cannot list goals for groups they don't teach => empty
    resp = client.get(
        '/api/goals/', {'group': other_teaching_group_with_members.id})
    assert resp.status_code == 200
    assert resp.json() == []

    # Teacher can list goals for students they teach
    #    - personal_goal
    #    - goal_with_group (group goal in a teaching group where student is member)
    resp = client.get('/api/goals/', {'student': student.id})
    assert resp.status_code == 200
    received_ids = {group['id'] for group in resp.json()}
    assert personal_goal.id in received_ids
    assert goal_with_group.id in received_ids
    # Should not include: personal_goal_other, group_goal_other
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

    # Teacher can retrieve a group goal in a group they teach
    resp = client.get(f'/api/goals/{goal_with_group.id}/')
    assert resp.status_code == 200

    # Teacher cannot retrieve goal created by teacher for unrelated student
    resp = client.get(f'/api/goals/{created_personal_goal.id}/')
    assert resp.status_code == 200

    # Teacher can retrieve personal goal for taught student
    resp = client.get(f'/api/goals/{personal_goal.id}/')
    assert resp.status_code == 200

    # Teacher cannot retrieve group goal for other group they do not teach
    resp = client.get(f'/api/goals/{group_goal_other.id}/')
    assert resp.status_code == 404

    # Teacher cannot retrieve personal goal for non-taught student
    resp = client.get(f'/api/goals/{personal_goal_other.id}/')
    assert resp.status_code == 404

    personal_goal_data = {
        'title': "New personal goal for student",
        'student_id': student.id,
        'subject_id': subject_without_group.id
    }

    # Teacher can create a personal goal for a student they teach
    resp = client.post('/api/goals/', personal_goal_data)
    assert resp.status_code == 201

    # Teacher cannot create a personal goal for a student they do not teach
    other_student_goal_data = {
        'title': "Goal for another student",
        'student_id': other_student.id,
        'subject_id': subject_without_group.id
    }
    resp = client.post('/api/goals/', other_student_goal_data)
    assert resp.status_code == 403

    # Teacher can create a group goal in a group they teach
    group_goal_data = {
        'title': "Group goal I should create",
        'group_id': goal_with_group.group.id
    }
    resp = client.post('/api/goals/', group_goal_data)
    assert resp.status_code == 201

    # Teacher cannot create a group goal in a group they do not teach
    other_group_goal_data = {
        'title': "Group goal I should not create",
        'group_id': other_teaching_group_with_members.id
    }
    resp = client.post('/api/goals/', other_group_goal_data)
    assert resp.status_code == 403

    # Teacher can update group goal in a group they teach
    resp = client.put(f'/api/goals/{goal_with_group.id}/', {
        'title': "Updated title for group goal",
    })
    assert resp.status_code == 200
    assert resp.json()['title'] == "Updated title for group goal"

    # Teacher cannot update group goal in a group they do not teach
    resp = client.put(f'/api/goals/{group_goal_other.id}/', {
        'title': "Updated title for other group",
    })
    assert resp.status_code == 403

    # Teacher can update personal goal for a student they teach
    resp = client.put(f'/api/goals/{personal_goal.id}/', {
        'title': "Updated title for personal goal",
    })
    assert resp.status_code == 200
    assert resp.json()['title'] == "Updated title for personal goal"

    # Teacher cannot update personal goal for a student they do not teach
    resp = client.put(f'/api/goals/{personal_goal_other.id}/', {
        'title': "Updated title for other student",
    })
    assert resp.status_code == 403

    # Teacher can delete group goal in a group they teach
    resp = client.delete(f'/api/goals/{goal_with_group.id}/')
    assert resp.status_code == 204

    # Teacher cannot delete group goal in a group they do not teach
    resp = client.delete(f'/api/goals/{group_goal_other.id}/')
    assert resp.status_code == 403

    # Teacher can delete personal goal for a student they teach
    resp = client.delete(f'/api/goals/{personal_goal.id}/')
    assert resp.status_code == 204

    # Teacher cannot delete personal goal for a student they do not teach
    resp = client.delete(f'/api/goals/{personal_goal_other.id}/')
    assert resp.status_code == 403
