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
def test_superadmin_goal_access(superadmin, goal_with_group, goal_individual_other_student):
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

    # Superadmin can list individual goals by subject
    resp = client.get(f'/api/goals/', {'subject': goal_individual_other_student.subject.id})
    assert resp.status_code == 200
    data = resp.json()
    received_ids = {goal['id'] for goal in data}
    expected_ids = {goal_individual_other_student.id}
    assert len(received_ids) == len(expected_ids)
    assert expected_ids.issubset(received_ids)

    # Surperadmin can retrieve a specific goal
    resp = client.get(f'/api/goals/{goal_with_group.id}/')
    assert resp.status_code == 200
    resp = client.get(f'/api/goals/{goal_individual_other_student.id}/')
    assert resp.status_code == 200


@pytest.mark.django_db
def test_school_inspector_goal_access(
        school_inspector, school, goal_with_group, goal_individual, goal_individual_other_student, student,
        teaching_group_with_members, other_teaching_group_with_members, other_school_teaching_group,
        other_school_student, other_school_group_goal, other_school_individual_goal, subject_owned_by_school,
        student_role):
    """
    Test access for school inspectors.
    School inspectors have read only access to all goals group and individual for students at their school
    They cannot create, update, or delete any goals
    """
    client = APIClient()
    client.force_authenticate(user=school_inspector)

    # Endpoint is unusable without required params
    resp = client.get('/api/goals/')
    assert resp.status_code == 400

    ################### List ###################

    # School inspector can list goals in groups at their school
    resp = client.get('/api/goals/', {'group': goal_with_group.group.id})
    assert resp.status_code == 200
    received_ids = {goal['id'] for goal in resp.json()}
    excepted_ids = {goal_with_group.id}
    assert received_ids == excepted_ids

    # School inspector cannot list goals in groups at other schools
    resp = client.get('/api/goals/', {'group': other_school_teaching_group.id})
    assert resp.status_code == 200
    assert resp.json() == []

    # School inspector can list goals for students at their school
    resp = client.get('/api/goals/', {'student': student.id})
    assert resp.status_code == 200
    received_ids = {goal['id'] for goal in resp.json()}
    excepted_ids = {goal_individual.id, goal_with_group.id}
    assert received_ids == excepted_ids

    # School inspector cannot list goals for students at other schools
    resp = client.get('/api/goals/', {'student': other_school_student.id})
    assert resp.status_code == 200
    assert resp.json() == []

    # School inspector can list goals by subject at their school
    resp = client.get('/api/goals/', {'subject': subject_owned_by_school.id})
    assert resp.status_code == 200
    received_ids = {goal['id'] for goal in resp.json()}
    excepted_ids = {goal_individual.id, goal_individual_other_student.id}
    assert received_ids == excepted_ids

    ################### Retrieve ###################

    # School inspector can retrieve goals at their school
    resp = client.get(f'/api/goals/{goal_with_group.id}/')
    assert resp.status_code == 200

    resp = client.get(f'/api/goals/{goal_individual.id}/')
    assert resp.status_code == 200

    # School inspector cannot retrieve goals at other schools
    resp = client.get(f'/api/goals/{other_school_group_goal.id}/')
    assert resp.status_code == 404

    resp = client.get(f'/api/goals/{other_school_individual_goal.id}/')
    assert resp.status_code == 404

    ################### Create ###################

    # School inspector has READ-ONLY access cannot create goals
    resp = client.post('/api/goals/', {
        'group_id': teaching_group_with_members.id,
        'title': 'New group goal by school inspector'
    }, format='json')
    assert resp.status_code == 403

    resp = client.post('/api/goals/', {
        'student_id': student.id,
        'title': 'New individual goal by school inspector',
        'subject_id': subject_owned_by_school.id
    }, format='json')
    assert resp.status_code == 403

    ################### Update ###################

    # School inspector cannot update goals
    resp = client.put(f'/api/goals/{goal_with_group.id}/', {
        'group_id': goal_with_group.group.id,
        'title': 'Updated goal title'
    }, format='json')
    assert resp.status_code == 403

    resp = client.put(f'/api/goals/{goal_individual.id}/', {
        'student_id': student.id,
        'title': 'Updated individual goal',
        'subject_id': subject_owned_by_school.id
    }, format='json')
    assert resp.status_code == 403

    ################### Delete ###################

    # School inspector cannot delete goals
    resp = client.delete(f'/api/goals/{goal_with_group.id}/')
    assert resp.status_code == 403

    resp = client.delete(f'/api/goals/{goal_individual.id}/')
    assert resp.status_code == 403


@pytest.mark.django_db
def test_student_goal_access(
    other_teaching_group_with_members,
    goal_with_group,
    subject_owned_by_school,
    student,
    other_student,
    teacher,
    school,
):
    client = APIClient()
    client.force_authenticate(user=student)

    # Individual goal owned by student
    individual_goal_self = Goal.objects.create(
        title="My individual goal",
        student=student,
        subject=subject_owned_by_school,
        school=school,
    )

    # Individual goal owned by another student
    individual_goal_other = Goal.objects.create(
        title="Other student individual goal",
        student=other_student,
        subject=subject_owned_by_school,
        school=school,
    )

    # Group goal in another group the student is NOT a member of
    group_goal_other = Goal.objects.create(
        title="Foreign group goal",
        group=other_teaching_group_with_members,
        school=school,
    )

    # Student can't list goals without required params
    resp = client.get('/api/goals/')
    assert resp.status_code == 400

    # Student can list individual and group goals
    # Should not include: individual_goal_other, group_goal_other
    resp = client.get('/api/goals/', {'student': student.id})
    assert resp.status_code == 200
    received_ids = {group['id'] for group in resp.json()}
    assert individual_goal_self.id in received_ids
    assert goal_with_group.id in received_ids
    assert individual_goal_other.id not in received_ids
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

    # Student can list individual goal by subject
    resp = client.get('/api/goals/', {'subject': subject_owned_by_school.id})
    assert resp.status_code == 200
    received_ids = {group['id'] for group in resp.json()}
    assert individual_goal_self.id in received_ids
    # Should not include other students goals nor group goals
    assert individual_goal_other.id not in received_ids
    assert goal_with_group.id not in received_ids

    # Student can retrieve own individual goal
    resp = client.get(f'/api/goals/{individual_goal_self.id}/')
    assert resp.status_code == 200

    # Student can retrieve group goal in own group
    resp = client.get(f'/api/goals/{goal_with_group.id}/')
    assert resp.status_code == 200

    # Student cannot retrieve other student's individual goal
    resp = client.get(f'/api/goals/{individual_goal_other.id}/')
    assert resp.status_code == 404

    # Student cannot retrieve foreign group goal -> 404
    resp = client.get(f'/api/goals/{group_goal_other.id}/')
    assert resp.status_code == 404

    # Student can CREATE individual goal for themselves
    resp = client.post('/api/goals/', {
        'student_id': student.id,
        'title': 'My new individual goal',
        'subject_id': subject_owned_by_school.id,
        'created_by_id': student.id,
        'school_id': school.id
    }, format='json')
    assert resp.status_code == 201
    created_goal_id = resp.json()['id']

    # Student cannot create individual goal for other students
    resp = client.post('/api/goals/', {
        'student_id': other_student.id,
        'title': 'Goal for other student',
        'subject_id': subject_owned_by_school.id,
        'created_by_id': student.id,
        'school_id': school.id
    }, format='json')
    assert resp.status_code == 403

    # Student cannot create group goal
    resp = client.post('/api/goals/', {
        'group_id': goal_with_group.group.id,
        'title': 'Group goal attempt',
        'created_by_id': student.id,
        'school_id': school.id
    }, format='json')
    assert resp.status_code == 403

    # Student can update their own individual goal if they have created it
    resp = client.put(f'/api/goals/{created_goal_id}/', {
        'student_id': student.id,
        'title': 'Updated individual goal',
        'subject_id': subject_owned_by_school.id,
        'school_id': school.id
    }, format='json')
    assert resp.status_code == 200

    # Student cannot update their own individual goal if teacher created it
    teacher_created_goal = Goal.objects.create(
        title="Teacher set goal for student",
        student=student,
        subject=subject_owned_by_school,
        created_by=teacher,
        school=school
    )
    resp = client.put(f'/api/goals/{teacher_created_goal.id}/', {
        'student_id': student.id,
        'title': 'Try to update teacher goal',
        'subject_id': subject_owned_by_school.id,
        'school_id': school.id
    }, format='json')
    assert resp.status_code == 403

    # Student cannot update other student's individual goal
    resp = client.put(f'/api/goals/{individual_goal_other.id}/', {
        'student_id': other_student.id,
        'title': "Can't update this",
        'subject_id': subject_owned_by_school.id,
        'school_id': school.id
    }, format='json')
    assert resp.status_code == 403

    # Student cannot update group goal
    resp = client.put(f'/api/goals/{goal_with_group.id}/', {
        'group_id': goal_with_group.group.id,
        'title': "Can't update group goal"
    }, format='json')
    assert resp.status_code == 403

    # Student can delete their own individual goal (that they created)
    resp = client.delete(f'/api/goals/{created_goal_id}/')
    assert resp.status_code == 204

    # Student cannot delete their own individual goal if teacher created it
    resp = client.delete(f'/api/goals/{teacher_created_goal.id}/')
    assert resp.status_code == 403

    # Student cannot delete other student's individual goal
    resp = client.delete(f'/api/goals/{individual_goal_other.id}/')
    assert resp.status_code == 403

    # Student cannot delete group goal
    resp = client.delete(f'/api/goals/{goal_with_group.id}/')
    assert resp.status_code == 403

    # Student without any group membership can still access their own individual goals
    student_without_groups = User.objects.create(
        name="Student without groups",
        feide_id="student-no-groups@example.com",
        email="student-no-groups@example.com",
    )
    individual_goal_no_groups = Goal.objects.create(
        title="Individual goal for student without groups",
        student=student_without_groups,
        subject=subject_owned_by_school,
        school=school
    )

    client.force_authenticate(user=student_without_groups)
    resp = client.get('/api/goals/', {'student': student_without_groups.id})
    assert resp.status_code == 200
    received_ids = {goal['id'] for goal in resp.json()}
    assert individual_goal_no_groups.id in received_ids


@pytest.mark.django_db
def test_teaching_group_teacher_goal_access(
    teacher,
    student,
    other_student,
    other_teacher,
    teaching_group_with_members,
    other_teaching_group_with_members,
    goal_with_group,
    subject_owned_by_school,
    subject_with_group,
    school
):
    """
    Test access for teachers who only teach a teaching group (NOT basis group teachers).
    Teaching group teachers have access to:
    - Can CRUD group goals in groups they teach
    - Can CRUD individual goals for students they teach in that subject
    - Cannot access individual goals in subjects they don't teach (e.g. social/behavioral subjects)
    """
    client = APIClient()
    client.force_authenticate(user=teacher)

    # Individual goal for student in subject teacher teaches
    individual_goal_in_taught_subject = Goal.objects.create(
        title="Student's individual goal in taught subject",
        student=student,
        subject=subject_with_group,
        school=school,
    )

    # Individual goal for student in subject teacher does NOT teach (e.g. social subject)
    individual_goal_untaught_subject = Goal.objects.create(
        title="Student's goal in subject teacher doesn't teach",
        student=student,
        subject=subject_owned_by_school,
        school=school,
    )

    # Individual goal for a student NOT in any group taught by teacher
    individual_goal_other = Goal.objects.create(
        title="Other student individual goal",
        student=other_student,
        subject=subject_owned_by_school,
        school=school,
    )

    # Group goal in a group teacher does NOT teach
    group_goal_other = Goal.objects.create(
        title="Foreign group goal",
        group=other_teaching_group_with_members,
        school=school,
    )

    # Endpoint is unusable without required params
    resp = client.get('/api/goals/')
    assert resp.status_code == 400

    # Endpoint is unusable with both group and subject params
    resp = client.get(
        '/api/goals/', {'group': teaching_group_with_members.id, 'subject': subject_owned_by_school.id})
    assert resp.status_code == 400

    # Can list goals in groups they teach
    resp = client.get('/api/goals/', {'group': teaching_group_with_members.id})
    assert resp.status_code == 200
    received_ids = {group['id'] for group in resp.json()}
    assert goal_with_group.id in received_ids
    assert group_goal_other.id not in received_ids
    assert individual_goal_in_taught_subject.id not in received_ids  # Not a group goal

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
    assert individual_goal_in_taught_subject.id in received_ids  # Individual goal in subject they teach
    assert individual_goal_untaught_subject.id not in received_ids
    assert individual_goal_other.id not in received_ids
    assert group_goal_other.id not in received_ids

    # Teacher cannot list goals of unaffiliated students
    resp = client.get('/api/goals/', {'student': other_student.id})
    assert resp.status_code == 200
    assert resp.json() == []

    # Teacher can list individual goals in subjects they teach
    resp = client.get('/api/goals/', {'subject': subject_with_group.id})
    assert resp.status_code == 200
    received_ids = {goal['id'] for goal in resp.json()}
    assert individual_goal_in_taught_subject.id in received_ids

    # Teacher can retrieve group goals they teach
    resp = client.get(f'/api/goals/{goal_with_group.id}/')
    assert resp.status_code == 200

    # Teacher can retrieve individual goals in subjects they teach
    resp = client.get(f'/api/goals/{individual_goal_in_taught_subject.id}/')
    assert resp.status_code == 200

    # Teacher cannot retrieve individual goals in subjects they don't teach (e.g. social subjects)
    resp = client.get(f'/api/goals/{individual_goal_untaught_subject.id}/')
    assert resp.status_code == 404

    # Teacher cannot retrieve goals in groups they don't teach
    resp = client.get(f'/api/goals/{group_goal_other.id}/')
    assert resp.status_code == 404

    # Teacher cannot retrieve other student's individual goals
    resp = client.get(f'/api/goals/{individual_goal_other.id}/')
    assert resp.status_code == 404

    # Teacher can create group goals in groups they teach
    resp = client.post('/api/goals/', {
        'group_id': teaching_group_with_members.id,
        'title': 'New group goal by teaching teacher',
        'created_by_id': teacher.id,
        'school_id': school.id
    }, format='json')
    assert resp.status_code == 201
    created_group_goal_id = resp.json()['id']

    # Teacher can create individual goals in subjects they teach
    resp = client.post('/api/goals/', {
        'student_id': student.id,
        'title': 'Individual goal in taught subject',
        'subject_id': teaching_group_with_members.subject.id,
        "created_by_id": teacher.id,
        'school_id': school.id
    }, format='json')
    assert resp.status_code == 201
    created_individual_goal_id = resp.json()['id']

    # Teacher cannot create individual goals in subjects they don't teach (e.g. social subjects)
    resp = client.post('/api/goals/', {
        'student_id': student.id,
        'title': 'Social goal attempt',
        'subject_id': subject_owned_by_school.id
    }, format='json')
    assert resp.status_code == 403

    # Teacher cannot create individual goals for students they don't teach
    resp = client.post('/api/goals/', {
        'student_id': other_student.id,
        'title': 'Goal for other student',
        'subject_id': teaching_group_with_members.subject.id
    }, format='json')
    assert resp.status_code == 403

    # Teacher can update group goals they teach
    resp = client.put(f'/api/goals/{created_group_goal_id}/', {
        'group_id': teaching_group_with_members.id,
        'title': 'Updated group goal',
        'school_id': school.id
    }, format='json')
    assert resp.status_code == 200
    assert resp.json()['title'] == 'Updated group goal'

    # Teacher can update individual goals in subjects they teach
    resp = client.put(f'/api/goals/{created_individual_goal_id}/', {
        'student_id': student.id,
        'title': 'Updated individual goal',
        'subject_id': teaching_group_with_members.subject.id,
        'school_id': school.id
    }, format='json')
    assert resp.status_code == 200
    assert resp.json()['title'] == 'Updated individual goal'

    # Teacher cannot update individual goals in subjects they don't teach
    resp = client.put(f'/api/goals/{individual_goal_untaught_subject.id}/', {
        'student_id': student.id,
        'title': 'Try to update social goal',
    }, format='json')
    assert resp.status_code == 403

    # Teacher can modify any group goals belonging to groups they teach
    goal_with_group.created_by = other_teacher
    goal_with_group.save()
    resp = client.put(f'/api/goals/{goal_with_group.id}/', {
        'group_id': teaching_group_with_members.id,
        'title': 'Try to update goal created by another teacher',
        'school_id': school.id
    }, format='json')
    assert resp.status_code == 200

    # Teacher can delete group goals they created
    resp = client.delete(f'/api/goals/{created_group_goal_id}/')
    assert resp.status_code == 204

    # Teacher can delete individual goals in subjects they teach
    resp = client.delete(f'/api/goals/{created_individual_goal_id}/')
    assert resp.status_code == 204

    # Teacher cannot delete individual goals in subjects they don't teach
    resp = client.delete(f'/api/goals/{individual_goal_untaught_subject.id}/')
    assert resp.status_code == 403

    # Teacher cannot update group goals in groups they don't teach
    resp = client.put(f'/api/goals/{group_goal_other.id}/', {
        'title': 'Try to update group goal not belonging to a group they teach'
    }, format='json')
    assert resp.status_code == 403

    # Teacher cannot delete group goals in groups they don't teach
    resp = client.delete(f'/api/goals/{group_goal_other.id}/')
    assert resp.status_code == 403


@pytest.mark.django_db
def test_basis_group_teacher_goal_access(
    teaching_group_with_members,
    other_teaching_group_with_members,
    basis_group,
    subject_owned_by_school,
    teacher,
    student,
    other_student,
    student_role,
    teacher_role,
    other_teacher,
    school,
):
    """
    Test access for basis group teachers.
    Basis group teachers have FULL access to their students:
    - Can see ALL goals (individual + group) for students in their basis group
    - Can see ALL goals (individual + group) for students in their basis group
    - Can see group goals in other teaching groups if student is in their basis group
    - Can modify individual goals only for students in their basis groups
    - Cannot modify group goals unless they also teach that group
    """
    client = APIClient()
    client.force_authenticate(user=teacher)

    # Make teacher a basis group teacher for student
    basis_group.add_member(student, student_role)
    basis_group.add_member(teacher, teacher_role)

    # Individual goal for student in teacher's basis group
    individual_goal = Goal.objects.create(
        title="Student's individual goal",
        student=student,
        subject=subject_owned_by_school,
        school=school,
    )

    # Individual goal for student not in teacher's basis group
    individual_goal_other = Goal.objects.create(
        title="Other student individual goal",
        student=other_student,
        subject=subject_owned_by_school,
        school=school,
    )

    # Group goal in teaching group teacher teaches
    group_goal_own = Goal.objects.create(
        title="Group goal in own teaching group",
        group=teaching_group_with_members,
        school=school,
    )

    # Student is also in another teaching group teacher doesn't teach
    other_teaching_group_with_members.add_member(student, student_role)
    group_goal_other = Goal.objects.create(
        title="Group goal in other teaching group",
        group=other_teaching_group_with_members,
        school=school,
    )

    # Basis teacher needs at least one parameter to list goals
    resp = client.get('/api/goals/')
    assert resp.status_code == 400

    # Basis teacher can see all goals (individual and group) for students in their basis group
    resp = client.get('/api/goals/', {'student': student.id})
    assert resp.status_code == 200
    received_ids = {goal['id'] for goal in resp.json()}
    assert individual_goal.id in received_ids
    assert group_goal_own.id in received_ids
    assert group_goal_other.id in received_ids
    assert individual_goal_other.id not in received_ids

    # Basis teacher can list individual goals by subject for their students
    resp = client.get('/api/goals/', {'subject': subject_owned_by_school.id})
    assert resp.status_code == 200
    received_ids = {goal['id'] for goal in resp.json()}
    assert individual_goal.id in received_ids
    assert individual_goal_other.id not in received_ids

    # Basis teacher can retrieve individual goals for their students
    resp = client.get(f'/api/goals/{individual_goal.id}/')
    assert resp.status_code == 200

    # Basis teacher can retrieve group goals for their students even in groups they don't teach
    resp = client.get(f'/api/goals/{group_goal_other.id}/')
    assert resp.status_code == 200

    # Basis teacher cannot retrieve individual goals for students outside their basis group
    resp = client.get(f'/api/goals/{individual_goal_other.id}/')
    assert resp.status_code == 404

    # Basis teacher can create individual goals for their students
    resp = client.post('/api/goals/', {
        'student_id': student.id,
        'title': 'Individual goal by basis teacher',
        'subject_id': subject_owned_by_school.id,
        'created_by_id': teacher.id,
        'school_id': school.id
    }, format='json')
    assert resp.status_code == 201
    created_individual_goal_id = resp.json()['id']

    # Basis teacher cannot create individual goals for students outside their basis group
    resp = client.post('/api/goals/', {
        'student_id': other_student.id,
        'title': 'Individual goal for other student',
        'subject_id': subject_owned_by_school.id,
        'school_id': school.id
    }, format='json')
    assert resp.status_code == 403

    # Basis teacher can update individual goals for their students
    resp = client.put(f'/api/goals/{created_individual_goal_id}/', {
        'student_id': student.id,
        'title': 'Updated individual goal',
        'subject_id': subject_owned_by_school.id,
        'school_id': school.id
    }, format='json')
    assert resp.status_code == 200
    assert resp.json()['title'] == 'Updated individual goal'

    # Basis teacher can modify individual goal created by student
    student_created_goal = Goal.objects.create(
        title="Student created their own goal",
        student=student,
        subject=subject_owned_by_school,
        created_by=student,
        school=school,
    )

    resp = client.put(f'/api/goals/{student_created_goal.id}/', {
        'student_id': student.id,
        'title': 'Teacher trying to update student goal',
        'subject_id': subject_owned_by_school.id,
        'school_id': school.id
    }, format='json')
    assert resp.status_code == 200

    resp = client.delete(f'/api/goals/{student_created_goal.id}/')
    assert resp.status_code == 204

    # Basis teacher cannot update group goals in groups they don't teach
    resp = client.put(f'/api/goals/{group_goal_other.id}/', {
        'title': "Can't update this",
        'school_id': school.id
    }, format='json')
    assert resp.status_code == 403

    # Basis teacher cannot delete group goals in groups they don't teach
    resp = client.delete(f'/api/goals/{group_goal_other.id}/')
    assert resp.status_code == 403

    # Basis teacher cannot update individual goals for students outside their basis group
    resp = client.put(f'/api/goals/{individual_goal_other.id}/', {
        'student_id': other_student.id,
        'title': 'Updated individual goal attempt',
        'subject_id': subject_owned_by_school.id,
        'school_id': school.id
    }, format='json')
    assert resp.status_code == 403

    # Basis teacher cannot delete individual goals for students outside their basis group
    resp = client.delete(f'/api/goals/{individual_goal_other.id}/')
    assert resp.status_code == 403

    # Basis group teacher can modify individual goals created by other teacher for their basis students
    other_teacher_in_same_group = User.objects.create(
        name="Otter Teacher",
        feide_id="otter-teacher-id@example.com",
        email="otter-teacher@example.com"
    )
    basis_group.add_member(other_teacher_in_same_group, teacher_role)

    goal_created_by_other_teacher = Goal.objects.create(
        title="Student created their own goal",
        student=student,
        subject=subject_owned_by_school,
        created_by=other_teacher_in_same_group,
        school=school,
    )
    resp = client.put(f'/api/goals/{goal_created_by_other_teacher.id}/', {
        'student_id': student.id,
        'title': 'Can update this',
        'subject_id': subject_owned_by_school.id,
        'school_id': school.id
    }, format='json')
    assert resp.status_code == 200

    # Basis group teacher can delete individual goals created by other teacher for their basis students
    resp = client.delete(f'/api/goals/{goal_created_by_other_teacher.id}/')
    assert resp.status_code == 204


@pytest.mark.django_db
def test_school_admin_goal_access(
    school_admin,
    school,
    other_school,
    teaching_group_with_members,
    other_school_teaching_group,
    goal_with_group,
    goal_individual,
    goal_individual_other_student,
    other_school_group_goal,
    other_school_individual_goal,
    subject_owned_by_school,
    student,
):
    """
    School admins have read and write access to goals at their school.
    They do not have access to goals from other schools.
    """
    client = APIClient()
    client.force_authenticate(user=school_admin)

    # Endpoint requires at least one param
    resp = client.get('/api/goals/')
    assert resp.status_code == 400

    # Can list group goals for groups at their school
    resp = client.get('/api/goals/', {'group': teaching_group_with_members.id})
    assert resp.status_code == 200
    received_ids = {goal['id'] for goal in resp.json()}
    expected_ids = {goal_with_group.id}
    assert received_ids == expected_ids

    # Cannot list group goals from other schools
    resp = client.get('/api/goals/', {'group': other_school_teaching_group.id})
    assert resp.status_code == 200
    assert resp.json() == []

    # Can list individual goals by subject owned by their school
    resp = client.get('/api/goals/', {'subject': subject_owned_by_school.id})
    assert resp.status_code == 200
    received_ids = {goal['id'] for goal in resp.json()}
    expected_ids = {goal_individual.id, goal_individual_other_student.id}
    assert received_ids == expected_ids

    # Can retrieve specific group and individual goals at their school
    resp = client.get(f'/api/goals/{goal_with_group.id}/')
    assert resp.status_code == 200
    resp = client.get(f'/api/goals/{goal_individual.id}/')
    assert resp.status_code == 200

    # Cannot retrieve goals from other schools
    resp = client.get(f'/api/goals/{other_school_group_goal.id}/')
    assert resp.status_code == 404
    resp = client.get(f'/api/goals/{other_school_individual_goal.id}/')
    assert resp.status_code == 404

    # Can create a group goal in their school
    resp = client.post('/api/goals/', {
        'group_id': teaching_group_with_members.id,
        'title': 'New group goal by school admin',
        'created_by_id': school_admin.id,
        'school_id': school.id
    }, format='json')
    assert resp.status_code == 201
    created_group_goal_id = resp.json()['id']

    # Can create a individual goal for a student in a subject owned by the school
    resp = client.post('/api/goals/', {
        'student_id': student.id,
        'title': 'New individual goal by school admin',
        'subject_id': subject_owned_by_school.id,
        'created_by_id': school_admin.id,
        'school_id': school.id
    }, format='json')
    assert resp.status_code == 201
    created_individual_goal_id = resp.json()['id']

    # Can update group goals at their school
    resp = client.put(f'/api/goals/{created_group_goal_id}/', {
        'group_id': teaching_group_with_members.id,
        'title': 'Updated by admin',
        'school_id': school.id
    }, format='json')
    assert resp.status_code == 200

    # Can update individual goals at their school
    resp = client.put(f'/api/goals/{created_individual_goal_id}/', {
        'student_id': student.id,
        'title': 'Updated individual by admin',
        'subject_id': subject_owned_by_school.id,
        'school_id': school.id
    }, format='json')
    assert resp.status_code == 200

    # Can delete goals at their school
    resp = client.delete(f'/api/goals/{created_group_goal_id}/')
    assert resp.status_code == 204
    resp = client.delete(f'/api/goals/{created_individual_goal_id}/')
    assert resp.status_code == 204

    # Cannot list goals from other schools
    resp = client.get('/api/goals/', {'group': other_school_teaching_group.id})
    assert resp.status_code == 200
    assert resp.json() == []

    # Cannot create goals for other schools' groups
    resp = client.post('/api/goals/', {
        'group_id': other_school_teaching_group.id,
        'title': 'Invalid group goal',
        'created_by_id': school_admin.id,
        'school_id': other_school.id
    }, format='json')
    assert resp.status_code == 403

    # Cannot update goals from other schools (403 or 404 depending on implementation)
    resp = client.put(f'/api/goals/{other_school_group_goal.id}/', {
        'group_id': other_school_teaching_group.id,
        'title': 'Try update other school'
    }, format='json')
    assert resp.status_code in (403, 404)
