import pytest
from rest_framework.test import APIClient
from mastery.models import User, UserSchool


@pytest.mark.django_db
def test_non_user_user_access(school, teaching_group_with_members, teacher, student):
    client = APIClient()
    # Non-authenticated user cannot access any users
    resp = client.get('/api/users/')
    assert resp.status_code == 403
    resp = client.get(f'/api/users/{teacher.id}/')
    assert resp.status_code == 403
    resp = client.get(f'/api/users/{student.id}/')
    assert resp.status_code == 403


@pytest.mark.django_db
def test_school_id_requirement(superadmin, student):
    client = APIClient()
    client.force_authenticate(user=superadmin)
    resp = client.get('/api/users/')
    assert resp.status_code == 400
    # school not required for retrieving a specific user
    resp = client.get(f'/api/users/{student.id}/')
    assert resp.status_code == 200


@pytest.mark.django_db
def test_superadmin_user_access(superadmin, school, teaching_group_with_members,
                                other_teaching_group_with_members):
    client = APIClient()
    client.force_authenticate(user=superadmin)

    # Can list all users in school
    resp = client.get('/api/users/', {'school': school.id})
    assert resp.status_code == 200
    data = resp.json()
    expected_ids = {user.id for user in teaching_group_with_members.get_members(
    )} | {user.id for user in other_teaching_group_with_members.get_members()}
    received_ids = {user['id'] for user in data}
    assert len(received_ids) == len(expected_ids)
    assert expected_ids.issubset(received_ids)

    # Can list all teachers in school
    resp = client.get('/api/users/', {'school': school.id, 'roles': 'teacher'})
    data = resp.json()
    expected_ids = {user.id for user in teaching_group_with_members.get_teachers(
    )} | {user.id for user in other_teaching_group_with_members.get_teachers()}
    received_ids = {user['id'] for user in data}
    assert len(received_ids) == len(expected_ids)
    assert expected_ids.issubset(received_ids)

    # Can list users by group
    resp = client.get(
        '/api/users/', {'school': school.id, 'groups': teaching_group_with_members.id})
    data = resp.json()
    expected_ids = {
        user.id for user in teaching_group_with_members.get_members()}
    received_ids = {user['id'] for user in data}
    assert len(received_ids) == len(expected_ids)
    assert expected_ids.issubset(received_ids)


@pytest.mark.django_db
def test_school_admin_user_access(
        school_admin, school, other_school, teaching_group_with_members,
        other_teaching_group_with_members, other_school_teaching_group_with_members,
        student_role, admin_role):
    """
    Test access for school admins.
    School admins can see ALL users (students and teachers) at their school,
    including users in groups they don't personally teach.
    They cannot see users from other schools.
    """
    client = APIClient()
    client.force_authenticate(user=school_admin)

    # Get users from admin's school
    teacher = teaching_group_with_members.get_teachers().first()
    student = teaching_group_with_members.get_students().first()
    other_teacher = other_teaching_group_with_members.get_teachers().first()
    other_student = other_teaching_group_with_members.get_students().first()

    # Get users from other school
    other_school_teacher = other_school_teaching_group_with_members.get_teachers().first()
    other_school_student = other_school_teaching_group_with_members.get_students().first()

    ################### List ###################

    # School admin can list ALL users at their school
    resp = client.get('/api/users/', {'school': school.id})
    assert resp.status_code == 200
    data = resp.json()

    # Expected users: all users in groups at the school + users directly affiliated via UserSchool
    expected_ids = (
        {user.id for user in teaching_group_with_members.get_members()} |
        {user.id for user in other_teaching_group_with_members.get_members()} |
        {user.id for user in school.get_affiliated_user(None)}
    )
    received_ids = {user['id'] for user in data}
    assert len(received_ids) == len(expected_ids)
    assert expected_ids.issubset(received_ids)

    # School admin can list all teachers at their school
    resp = client.get('/api/users/', {'school': school.id, 'roles': 'teacher'})
    assert resp.status_code == 200
    data = resp.json()
    expected_ids = {teacher.id, other_teacher.id}
    received_ids = {user['id'] for user in data}
    assert len(received_ids) == len(expected_ids)
    assert expected_ids.issubset(received_ids)

    # School admin can list all students at their school
    resp = client.get('/api/users/', {'school': school.id, 'roles': 'student'})
    assert resp.status_code == 200
    data = resp.json()
    expected_ids = {student.id, other_student.id}
    received_ids = {user['id'] for user in data}
    assert len(received_ids) == len(expected_ids)
    assert expected_ids.issubset(received_ids)

    # School admin can list users in specific groups at their school
    resp = client.get('/api/users/', {'school': school.id, 'groups': teaching_group_with_members.id})
    assert resp.status_code == 200
    data = resp.json()
    expected_ids = {teacher.id, student.id}
    received_ids = {user['id'] for user in data}
    assert len(received_ids) == len(expected_ids)
    assert expected_ids.issubset(received_ids)

    # School admin cannot list users from other schools
    resp = client.get('/api/users/', {'school': other_school.id})
    assert resp.status_code == 200
    data = resp.json()
    # Should only see themselves if they have direct school affiliation, otherwise empty
    assert other_school_teacher.id not in {user['id'] for user in data}
    assert other_school_student.id not in {user['id'] for user in data}

    ################### Retrieve ###################

    # School admin can retrieve students at their school
    resp = client.get(f'/api/users/{student.id}/')
    assert resp.status_code == 200

    resp = client.get(f'/api/users/{other_student.id}/')
    assert resp.status_code == 200

    # School admin can retrieve teachers at their school
    resp = client.get(f'/api/users/{teacher.id}/')
    assert resp.status_code == 200

    resp = client.get(f'/api/users/{other_teacher.id}/')
    assert resp.status_code == 200

    # School admin can retrieve themselves
    resp = client.get(f'/api/users/{school_admin.id}/')
    assert resp.status_code == 200

    # School admin cannot retrieve users from other schools
    resp = client.get(f'/api/users/{other_school_teacher.id}/')
    assert resp.status_code == 404

    resp = client.get(f'/api/users/{other_school_student.id}/')
    assert resp.status_code == 404

    ################### UserSchool affiliated student ###################

    # Teacher becomes school admin
    teacher_becomes_school_admin = UserSchool.objects.create(
        user=teacher, school=school, role=admin_role
    )

    client.force_authenticate(user=teacher)
    # Now teacher (as school admin) can see all users at the school
    resp = client.get('/api/users/', {'school': school.id})
    assert resp.status_code == 200
    data = resp.json()
    expected_ids = (
        {user.id for user in teaching_group_with_members.get_members()} |
        {user.id for user in other_teaching_group_with_members.get_members()} |
        {user.id for user in school.get_affiliated_user(None)}
    )
    received_ids = {user['id'] for user in data}
    assert len(received_ids) == len(expected_ids)
    assert expected_ids.issubset(received_ids)


@pytest.mark.django_db
def test_user_self_access(teaching_group_with_members, school):
    client = APIClient()
    teacher = teaching_group_with_members.get_teachers().first()
    student = teaching_group_with_members.get_students().first()

    for user in [teacher, student]:
        client.force_authenticate(user=user)

        # Students and teachers can list users in their groups
        resp = client.get('/api/users/', {'school': school.id})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        expected_ids = {teacher.id, student.id}
        assert {user.id}.issubset(expected_ids)

        # User can retrieve self
        resp = client.get(f'/api/users/{user.id}/')
        assert resp.status_code == 200


@pytest.mark.django_db
def test_teacher_user_access(
        school, teaching_group_with_members, other_teaching_group_with_members,
        other_school_teaching_group_with_members):
    teacher = teaching_group_with_members.get_teachers().first()
    student = teaching_group_with_members.get_students().first()
    other_teacher = other_teaching_group_with_members.get_teachers().first()
    other_student = other_teaching_group_with_members.get_students().first()

    client = APIClient()
    client.force_authenticate(user=teacher)

    # Teacher cannot retrieve unaffiliated student
    resp = client.get(f'/api/users/{other_student.id}/')
    assert resp.status_code == 404

    # Teacher can retrieve student if in group
    resp = client.get(f'/api/users/{student.id}/')
    assert resp.status_code == 200

    # Teacher can retrieve other teacher
    resp = client.get(f'/api/users/{other_teacher.id}/')
    assert resp.status_code == 200

    # Teacher can list users at their school
    resp = client.get('/api/users/', {'school': school.id})
    assert resp.status_code == 200
    data = resp.json()
    expected_ids = {teacher.id, student.id, other_teacher.id}
    received_ids = {user['id'] for user in data}
    assert len(received_ids) == len(expected_ids)
    assert expected_ids.issubset(received_ids)

    # Teacher can list users in their groups
    resp = client.get(
        '/api/users/', {'school': school.id, 'groups': teaching_group_with_members.id})
    assert resp.status_code == 200
    data = resp.json()
    expected_ids = {teacher.id, student.id}
    received_ids = {user['id'] for user in data}
    assert len(received_ids) == len(expected_ids)
    assert expected_ids.issubset(received_ids)

    # Teacher cannot retrieve teacher from other school
    other_school_teacher = other_school_teaching_group_with_members.get_teachers().first()
    resp = client.get(f'/api/users/{other_school_teacher.id}/')
    assert resp.status_code == 404

    # Teacher cannot retrieve student from other school
    other_school_student = other_school_teaching_group_with_members.get_students().first()
    resp = client.get(f'/api/users/{other_school_student.id}/')
    assert resp.status_code == 404


@pytest.mark.django_db
def test_student_user_access(
        school, student_role, teaching_group_with_members, other_teaching_group_with_members,
        other_school_teaching_group_with_members):
    teacher = teaching_group_with_members.get_teachers().first()
    student = teaching_group_with_members.get_students().first()
    other_teacher = other_teaching_group_with_members.get_teachers().first()
    other_student = other_teaching_group_with_members.get_students().first()

    client = APIClient()
    client.force_authenticate(user=student)

    # Student can retrieve other teacher
    resp = client.get(f'/api/users/{other_teacher.id}/')
    assert resp.status_code == 200

    # Student can list teachers at their school
    resp = client.get('/api/users/', {'school': school.id, 'roles': 'teacher'})
    assert resp.status_code == 200
    data = resp.json()
    expected_ids = {teacher.id, other_teacher.id}
    received_ids = {user['id'] for user in data}
    assert len(received_ids) == len(expected_ids)
    assert expected_ids.issubset(received_ids)

    # Student can list users in their groups
    resp = client.get(
        '/api/users/', {'school': school.id, 'groups': teaching_group_with_members.id})
    assert resp.status_code == 200
    data = resp.json()
    expected_ids = {teacher.id, student.id}
    received_ids = {user['id'] for user in data}
    assert len(received_ids) == len(expected_ids)
    assert expected_ids.issubset(received_ids)

    # Student cannot retrieve unaffiliated student
    resp = client.get(f'/api/users/{other_student.id}/')
    assert resp.status_code == 404

    # Student can retrieve student if in group
    teaching_group_with_members.add_member(other_student, student_role)
    resp = client.get(f'/api/users/{other_student.id}/')
    assert resp.status_code == 200

    # Student cannot retrieve teacher from other school
    other_school_teacher = other_school_teaching_group_with_members.get_teachers().first()
    resp = client.get(f'/api/users/{other_school_teacher.id}/')
    assert resp.status_code == 404

    # Student cannot retrieve student from other school
    other_school_student = other_school_teaching_group_with_members.get_students().first()
    resp = client.get(f'/api/users/{other_school_student.id}/')
    assert resp.status_code == 404
