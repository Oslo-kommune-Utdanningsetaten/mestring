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
def test_school_admin_goal_access(
        school_admin, school, goal_with_group, goal_personal, goal_personal_other_student, student,
        teaching_group_with_members, other_teaching_group_with_members, other_school_teaching_group,
        other_school_student, other_school_group_goal, other_school_personal_goal, subject_without_group,
        student_role):
    """
    Test access for school admins.
    School admins have read only access to all goals group and personal for students at their school
    They cannot create, update, or delete any goals
    """
    client = APIClient()
    client.force_authenticate(user=school_admin)

    ################### Setup ###################

    # Unaffiliated student not in any group
    unaffiliated_student = User.objects.create(
        name="Unaffiliated Student",
        feide_id="unaffiliated-student@example.com",
        email="unaffiliated-student@example.com",
    )
    personal_goal_unaffiliated = Goal.objects.create(
        title="Personal goal for unaffiliated student",
        student=unaffiliated_student,
        subject=subject_without_group,
    )

    # Endpoint is unusable without required params
    resp = client.get('/api/goals/')
    assert resp.status_code == 400

    ################### List ###################

    # School admin can list goals in groups at their school
    resp = client.get('/api/goals/', {'group': goal_with_group.group.id})
    assert resp.status_code == 200
    received_ids = {goal['id'] for goal in resp.json()}
    assert goal_with_group.id in received_ids
    assert other_school_group_goal.id not in received_ids

    # School admin cannot list goals in groups at other schools
    resp = client.get('/api/goals/', {'group': other_school_teaching_group.id})
    assert resp.status_code == 200
    assert resp.json() == []

    # School admin can list goals for students at their school
    resp = client.get('/api/goals/', {'student': student.id})
    assert resp.status_code == 200
    received_ids = {goal['id'] for goal in resp.json()}
    assert goal_personal.id in received_ids  # Personal goal at admin's school
    assert goal_with_group.id in received_ids  # Group goal at admin's school
    assert other_school_personal_goal.id not in received_ids
    assert personal_goal_unaffiliated.id not in received_ids

    # School admin cannot list goals for students at other schools
    resp = client.get('/api/goals/', {'student': other_school_student.id})
    assert resp.status_code == 200
    assert resp.json() == []

    # School admin cannot list goals for unaffiliated students
    resp = client.get('/api/goals/', {'student': unaffiliated_student.id})
    assert resp.status_code == 200
    assert resp.json() == []

    # School admin can list goals by subject at their school
    resp = client.get('/api/goals/', {'subject': subject_without_group.id})
    assert resp.status_code == 200
    received_ids = {goal['id'] for goal in resp.json()}
    assert goal_personal.id not in received_ids  # Fails because it don´t have subject
    assert goal_personal_other_student.id in received_ids
    assert other_school_personal_goal.id not in received_ids
    assert personal_goal_unaffiliated.id not in received_ids

    ################### Retrieve ###################

    # School admin can retrieve goals at their school
    resp = client.get(f'/api/goals/{goal_with_group.id}/')
    assert resp.status_code == 200

    resp = client.get(f'/api/goals/{goal_personal.id}/')
    assert resp.status_code == 200

    # School admin cannot retrieve goals at other schools
    resp = client.get(f'/api/goals/{other_school_group_goal.id}/')
    assert resp.status_code == 404

    resp = client.get(f'/api/goals/{other_school_personal_goal.id}/')
    assert resp.status_code == 404

    resp = client.get(f'/api/goals/{personal_goal_unaffiliated.id}/')
    assert resp.status_code == 404

    ################### Create ###################

    # School admin has READ-ONLY access cannot create goals
    resp = client.post('/api/goals/', {
        'group_id': teaching_group_with_members.id,
        'title': 'New group goal by school admin'
    }, format='json')
    assert resp.status_code == 403

    resp = client.post('/api/goals/', {
        'student_id': student.id,
        'title': 'New personal goal by school admin',
        'subject_id': subject_without_group.id
    }, format='json')
    assert resp.status_code == 403

    ################### Update ###################

    # School admin cannot update goals
    resp = client.put(f'/api/goals/{goal_with_group.id}/', {
        'group_id': goal_with_group.group.id,
        'title': 'Updated goal title'
    }, format='json')
    assert resp.status_code == 403

    resp = client.put(f'/api/goals/{goal_personal.id}/', {
        'student_id': student.id,
        'title': 'Updated personal goal',
        'subject_id': subject_without_group.id
    }, format='json')
    assert resp.status_code == 403

    ################### Delete ###################

    # School admin cannot delete goals
    resp = client.delete(f'/api/goals/{goal_with_group.id}/')
    assert resp.status_code == 403

    resp = client.delete(f'/api/goals/{goal_personal.id}/')
    assert resp.status_code == 403

    ################### User School affiliation ###################

    # Student directly affiliated with school via UserSchool
    student_via_user_school = User.objects.create(
        name="Direct Affiliated Student",
        feide_id="direct-student@example.com",
        email="direct-student@example.com",
    )
    school.set_affiliated_user(student_via_user_school, student_role)
    personal_goal_direct_student = Goal.objects.create(
        title="Personal goal for directly affiliated student",
        student=student_via_user_school,
        subject=subject_without_group,
    )

    # School admin should be able to see this goal
    resp = client.get('/api/goals/', {'student': student_via_user_school.id})
    assert resp.status_code == 200
    assert personal_goal_direct_student.id in {goal['id'] for goal in resp.json()}


@pytest.mark.django_db
def test_student_goal_access(
    other_teaching_group_with_members,
    goal_with_group,
    subject_without_group,
    student,
    other_student,
    teacher,
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
        'subject_id': subject_without_group.id,
        'created_by_id': student.id
    }, format='json')
    assert resp.status_code == 201
    created_goal_id = resp.json()['id']

    # Student cannot create personal goal for other students
    resp = client.post('/api/goals/', {
        'student_id': other_student.id,
        'title': 'Goal for other student',
        'subject_id': subject_without_group.id,
        'created_by_id': student.id
    }, format='json')
    assert resp.status_code == 403

    # Student cannot create group goal
    resp = client.post('/api/goals/', {
        'group_id': goal_with_group.group.id,
        'title': 'Group goal attempt',
        'created_by_id': student.id
    }, format='json')
    assert resp.status_code == 403

    # Student can update their own personal goal if they have created it
    resp = client.put(f'/api/goals/{created_goal_id}/', {
        'student_id': student.id,
        'title': 'Updated personal goal',
        'subject_id': subject_without_group.id
    }, format='json')
    assert resp.status_code == 200

    # Student cannot update their own personal goal if teacher created it
    teacher_created_goal = Goal.objects.create(
        title="Teacher set goal for student",
        student=student,
        subject=subject_without_group,
        created_by=teacher,
    )
    resp = client.put(f'/api/goals/{teacher_created_goal.id}/', {
        'student_id': student.id,
        'title': 'Try to update teacher goal',
        'subject_id': subject_without_group.id
    }, format='json')
    assert resp.status_code == 403

    # Student cannot update other student's personal goal
    resp = client.put(f'/api/goals/{personal_goal_other.id}/', {
        'student_id': other_student.id,
        'title': "Can't update this",
        'subject_id': subject_without_group.id
    }, format='json')
    assert resp.status_code == 403

    # Student cannot update group goal
    resp = client.put(f'/api/goals/{goal_with_group.id}/', {
        'group_id': goal_with_group.group.id,
        'title': "Can't update group goal"
    }, format='json')
    assert resp.status_code == 403

    # Student can delete their own personal goal (that they created)
    resp = client.delete(f'/api/goals/{created_goal_id}/')
    assert resp.status_code == 204

    # Student cannot delete their own personal goal if teacher created it
    resp = client.delete(f'/api/goals/{teacher_created_goal.id}/')
    assert resp.status_code == 403

    # Student cannot delete other student's personal goal
    resp = client.delete(f'/api/goals/{personal_goal_other.id}/')
    assert resp.status_code == 403

    # Student cannot delete group goal
    resp = client.delete(f'/api/goals/{goal_with_group.id}/')
    assert resp.status_code == 403

    # Student without any group membership can still access their own personal goals
    student_without_groups = User.objects.create(
        name="Student without groups",
        feide_id="student-no-groups@example.com",
        email="student-no-groups@example.com",
    )
    personal_goal_no_groups = Goal.objects.create(
        title="Personal goal for student without groups",
        student=student_without_groups,
        subject=subject_without_group,
    )

    client.force_authenticate(user=student_without_groups)
    resp = client.get('/api/goals/', {'student': student_without_groups.id})
    assert resp.status_code == 200
    received_ids = {goal['id'] for goal in resp.json()}
    assert personal_goal_no_groups.id in received_ids


@pytest.mark.django_db
def test_teaching_group_teacher_goal_access(
    teaching_group_with_members,
    other_teaching_group_with_members,
    goal_with_group,
    subject_without_group,
    subject_with_group,
    teacher,
    student,
    other_student,
    other_teacher,
):
    """
    Test access for teachers who only teach a teaching group (NOT basis group teachers).
    Teaching group teachers have access to:
    - Can CRUD group goals in groups they teach
    - Can CRUD personal goals for students they teach in that subject
    - Cannot access personal goals in subjects they don't teach (e.g. social/behavioral subjects)
    - Can see goals they created (regardless of student affiliation)
    """
    client = APIClient()
    client.force_authenticate(user=teacher)

    # Personal goal for student in subject teacher teaches
    personal_goal_in_taught_subject = Goal.objects.create(
        title="Student's personal goal in taught subject",
        student=student,
        subject=subject_with_group,
    )

    # Personal goal for student in subject teacher does NOT teach (e.g. social subject)
    personal_goal_untaught_subject = Goal.objects.create(
        title="Student's goal in subject teacher doesn't teach",
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
    assert personal_goal_in_taught_subject.id not in received_ids  # Not a group goal

    # Teacher can't list goals for groups they don't teach => empty
    resp = client.get(
        '/api/goals/', {'group': other_teaching_group_with_members.id})
    assert resp.status_code == 200
    assert resp.json() == []

    # Teacher can list goals for students they teach
    resp = client.get('/api/goals/', {'student': student.id})
    assert resp.status_code == 200
    received_ids = {goal['id'] for goal in resp.json()}
    assert goal_with_group.id in received_ids  # Group goal
    assert personal_goal_in_taught_subject.id in received_ids  # Personal goal in subject they teach
    assert personal_goal_untaught_subject.id not in received_ids
    assert personal_goal_other.id not in received_ids
    assert group_goal_other.id not in received_ids

    # Teacher cannot list goals of unaffiliated students
    resp = client.get('/api/goals/', {'student': other_student.id})
    assert resp.status_code == 200
    assert resp.json() == []

    # Teacher can list personal goals in subjects they teach
    resp = client.get('/api/goals/', {'subject': subject_with_group.id})
    assert resp.status_code == 200
    received_ids = {goal['id'] for goal in resp.json()}
    assert personal_goal_in_taught_subject.id in received_ids

    # Teacher can list goals they created (even in subjects they don't teach)
    resp = client.get('/api/goals/', {'subject': subject_without_group.id})
    assert resp.status_code == 200
    received_ids = {goal['id'] for goal in resp.json()}
    assert created_personal_goal.id in received_ids
    assert personal_goal_other.id not in received_ids
    assert personal_goal_untaught_subject.id not in received_ids  # Not created by teacher

    # Teacher can retrieve group goals they teach
    resp = client.get(f'/api/goals/{goal_with_group.id}/')
    assert resp.status_code == 200

    # Teacher can retrieve personal goals in subjects they teach
    resp = client.get(f'/api/goals/{personal_goal_in_taught_subject.id}/')
    assert resp.status_code == 200

    # Teacher cannot retrieve personal goals in subjects they don't teach (e.g. social subjects)
    resp = client.get(f'/api/goals/{personal_goal_untaught_subject.id}/')
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
        'title': 'New group goal by teaching teacher',
        "created_by_id": teacher.id
    }, format='json')
    assert resp.status_code == 201
    created_group_goal_id = resp.json()['id']

    # Teacher can create personal goals in subjects they teach
    resp = client.post('/api/goals/', {
        'student_id': student.id,
        'title': 'Personal goal in taught subject',
        'subject_id': teaching_group_with_members.subject.id,
        "created_by_id": teacher.id
    }, format='json')
    assert resp.status_code == 201
    created_personal_goal_id = resp.json()['id']

    # Teacher cannot create personal goals in subjects they don't teach (e.g. social subjects)
    resp = client.post('/api/goals/', {
        'student_id': student.id,
        'title': 'Social goal attempt',
        'subject_id': subject_without_group.id
    }, format='json')
    assert resp.status_code == 403

    # Teacher cannot create personal goals for students they don't teach
    resp = client.post('/api/goals/', {
        'student_id': other_student.id,
        'title': 'Goal for other student',
        'subject_id': teaching_group_with_members.subject.id
    }, format='json')
    assert resp.status_code == 403

    # Teacher can update group goals they teach
    resp = client.put(f'/api/goals/{created_group_goal_id}/', {
        'group_id': teaching_group_with_members.id,
        'title': 'Updated group goal'
    }, format='json')
    assert resp.status_code == 200
    assert resp.json()['title'] == 'Updated group goal'

    # Teacher can update personal goals in subjects they teach
    resp = client.put(f'/api/goals/{created_personal_goal_id}/', {
        'student_id': student.id,
        'title': 'Updated personal goal',
        'subject_id': teaching_group_with_members.subject.id
    }, format='json')
    assert resp.status_code == 200
    assert resp.json()['title'] == 'Updated personal goal'

    # Teacher cannot update personal goals in subjects they don't teach
    resp = client.put(f'/api/goals/{personal_goal_untaught_subject.id}/', {
        'student_id': student.id,
        'title': 'Try to update social goal',
        'subject_id': subject_without_group.id
    }, format='json')
    assert resp.status_code == 403

    # Teacher cannot update group goals they didn't create even in groups they teach
    goal_with_group.created_by = other_teacher
    goal_with_group.save()
    resp = client.put(f'/api/goals/{goal_with_group.id}/', {
        'group_id': teaching_group_with_members.id,
        'title': 'Try to update goal created by another teacher'
    }, format='json')
    assert resp.status_code == 403

    # Teacher can delete group goals they created
    resp = client.delete(f'/api/goals/{created_group_goal_id}/')
    assert resp.status_code == 204

    # Teacher can delete personal goals in subjects they teach
    resp = client.delete(f'/api/goals/{created_personal_goal_id}/')
    assert resp.status_code == 204

    # Teacher cannot delete personal goals in subjects they don't teach
    resp = client.delete(f'/api/goals/{personal_goal_untaught_subject.id}/')
    assert resp.status_code == 403

    # Teacher cannot delete group goals in groups they don't teach
    resp = client.delete(f'/api/goals/{group_goal_other.id}/')
    assert resp.status_code == 403


@pytest.mark.django_db
def test_basis_group_teacher_goal_access(
    teaching_group_with_members,
    other_teaching_group_with_members,
    basis_group,
    subject_without_group,
    teacher,
    student,
    other_student,
    student_role,
    teacher_role,
    other_teacher
):
    """
    Test access for basis group teachers.
    Basis group teachers have FULL access to their students:
    - Can see ALL goals (personal + group) for students in their basis group
    - Can CRUD personal goals for their basis students
    - Can see (but not modify) group goals in other teaching groups if student is in their basis group
    - Cannot modify group goals unless they also teach that group
    - Cannot modify personal goals they did not create
    """
    client = APIClient()
    client.force_authenticate(user=teacher)

    # Make teacher a basis group teacher for student
    basis_group.add_member(student, student_role)
    basis_group.add_member(teacher, teacher_role)

    # Personal goal for student in teacher's basis group
    personal_goal = Goal.objects.create(
        title="Student's personal goal",
        student=student,
        subject=subject_without_group,
    )

    # Personal goal for student not in teacher's basis group
    personal_goal_other = Goal.objects.create(
        title="Other student personal goal",
        student=other_student,
        subject=subject_without_group,
    )

    # Group goal in teaching group teacher teaches
    group_goal_own = Goal.objects.create(
        title="Group goal in own teaching group",
        group=teaching_group_with_members,
    )

    # Student is also in another teaching group teacher doesn't teach
    other_teaching_group_with_members.add_member(student, student_role)
    group_goal_other = Goal.objects.create(
        title="Group goal in other teaching group",
        group=other_teaching_group_with_members,
    )

    # Basis teacher needs at least one parameter to list goals
    resp = client.get('/api/goals/')
    assert resp.status_code == 400

    # Basis teacher can see all goals (personal and group) for students in their basis group
    resp = client.get('/api/goals/', {'student': student.id})
    assert resp.status_code == 200
    received_ids = {goal['id'] for goal in resp.json()}
    assert personal_goal.id in received_ids
    assert group_goal_own.id in received_ids
    assert group_goal_other.id in received_ids
    assert personal_goal_other.id not in received_ids

    # Basis teacher can list personal goals by subject for their students
    resp = client.get('/api/goals/', {'subject': subject_without_group.id})
    assert resp.status_code == 200
    received_ids = {goal['id'] for goal in resp.json()}
    assert personal_goal.id in received_ids
    assert personal_goal_other.id not in received_ids

    # Basis teacher can retrieve personal goals for their students
    resp = client.get(f'/api/goals/{personal_goal.id}/')
    assert resp.status_code == 200

    # Basis teacher can retrieve group goals for their students even in groups they don't teach
    resp = client.get(f'/api/goals/{group_goal_other.id}/')
    assert resp.status_code == 200

    # Basis teacher cannot retrieve personal goals for students outside their basis group
    resp = client.get(f'/api/goals/{personal_goal_other.id}/')
    assert resp.status_code == 404

    # Basis teacher can create personal goals for their students
    resp = client.post('/api/goals/', {
        'student_id': student.id,
        'title': 'Personal goal by basis teacher',
        'subject_id': subject_without_group.id,
        'created_by_id': teacher.id
    }, format='json')
    assert resp.status_code == 201
    created_personal_goal_id = resp.json()['id']

    # Basis teacher cannot create personal goals for students outside their basis group
    resp = client.post('/api/goals/', {
        'student_id': other_student.id,
        'title': 'Personal goal for other student',
        'subject_id': subject_without_group.id
    }, format='json')
    assert resp.status_code == 403

    # Basis teacher can update personal goals for their students they created
    resp = client.put(f'/api/goals/{created_personal_goal_id}/', {
        'student_id': student.id,
        'title': 'Updated personal goal',
        'subject_id': subject_without_group.id
    }, format='json')
    assert resp.status_code == 200
    assert resp.json()['title'] == 'Updated personal goal'

    # Basis teacher cannot modify personal goal created by student
    student_created_goal = Goal.objects.create(
        title="Student created their own goal",
        student=student,
        subject=subject_without_group,
        created_by=student,
    )

    resp = client.put(f'/api/goals/{student_created_goal.id}/', {
        'student_id': student.id,
        'title': 'Teacher trying to update student goal',
        'subject_id': subject_without_group.id
    }, format='json')
    assert resp.status_code == 403

    resp = client.delete(f'/api/goals/{student_created_goal.id}/')
    assert resp.status_code == 403

    # Basis teacher cannot update group goals in groups they don't teach
    resp = client.put(f'/api/goals/{group_goal_other.id}/', {
        'group_id': other_teaching_group_with_members.id,
        'title': "Can't update this"
    }, format='json')
    assert resp.status_code == 403

    # Basis teacher cannot update personal goals for students outside their basis group
    resp = client.put(f'/api/goals/{personal_goal_other.id}/', {
        'student_id': other_student.id,
        'title': 'Updated personal goal attempt',
        'subject_id': subject_without_group.id
    }, format='json')
    assert resp.status_code == 403

    # Basis teacher can delete personal goals for their students they created
    resp = client.delete(f'/api/goals/{created_personal_goal_id}/')
    assert resp.status_code == 204

    # Basis teacher cannot delete group goals in groups they don't teach
    resp = client.delete(f'/api/goals/{group_goal_other.id}/')
    assert resp.status_code == 403

    # Basis teacher cannot delete personal goals for students outside their basis group
    resp = client.delete(f'/api/goals/{personal_goal_other.id}/')
    assert resp.status_code == 403

    personal_goal_other_teahcer = Goal.objects.create(
        title="Other student personal goal",
        student=student,
        subject=subject_without_group,
        created_by=other_teacher,
    )

    # Basis group teacher cannot modify personal goal they did not create
    resp = client.put(f'/api/goals/{personal_goal_other_teahcer.id}/', {
        'student_id': student.id,
        'title': 'Cannot update this',
        'subject_id': subject_without_group.id
    }, format='json')
    assert resp.status_code == 403

    resp = client.delete(f'/api/goals/{personal_goal_other_teahcer.id}/')
    assert resp.status_code == 403
