import pytest
from rest_framework.test import APIClient
from mastery.models import Group, User


@pytest.mark.django_db
def test_non_user_group_access(school, teaching_group_with_members, teaching_group_without_members):
    client = APIClient()
    # Non-authenticated user cannot access groups
    resp = client.get('/api/groups/')
    assert resp.status_code == 403
    resp = client.get(f'/api/groups/{teaching_group_with_members.id}/')
    assert resp.status_code == 403
    resp = client.get(f'/api/groups/{teaching_group_without_members.id}/')
    assert resp.status_code == 403


@pytest.mark.django_db
def test_school_id_requirement(school, superadmin, teaching_group_with_members):
    client = APIClient()
    client.force_authenticate(user=superadmin)
    # School ID is required for listing groups
    resp = client.get('/api/groups/')
    assert resp.status_code == 400
    # Listing groups with school ID
    resp = client.get('/api/groups/', {'school': school.id})
    assert resp.status_code == 200
    # School not required for retrieving a specific group
    resp = client.get(f'/api/groups/{teaching_group_with_members.id}/')
    assert resp.status_code == 200


@pytest.mark.django_db
def test_superadmin_group_access(
        school, teaching_group_with_members, other_teaching_group_with_members, disabled_group, superadmin):
    client = APIClient()
    client.force_authenticate(user=superadmin)

    # Can list all groups, including disabled ones
    resp = client.get('/api/groups/', {'school': school.id, 'enabled': 'include'})
    assert resp.status_code == 200
    data = resp.json()
    expected_ids = {teaching_group_with_members.id,
                    other_teaching_group_with_members.id, disabled_group.id}
    received_ids = {group['id'] for group in data}
    assert len(received_ids) == len(expected_ids)
    assert expected_ids.issubset(received_ids)

    # Can list only disabled groups
    resp = client.get('/api/groups/', {'school': school.id, 'enabled': 'exclude'})
    assert resp.status_code == 200
    data = resp.json()
    expected_ids = {disabled_group.id}
    received_ids = {group['id'] for group in data}
    assert len(received_ids) == len(expected_ids)
    assert expected_ids.issubset(received_ids)

    # Create another group and verify superadmin sees it too
    a_group = Group.objects.create(
        feide_id="fc:group:other",
        display_name="Nother Group",
        type="basis",
        school=school,
        is_enabled=True
    )
    # Group listing should include new group
    resp = client.get('/api/groups/', {'school': school.id, 'enabled': 'include'})
    assert resp.status_code == 200
    data = resp.json()
    expected_ids = {teaching_group_with_members.id,
                    other_teaching_group_with_members.id, disabled_group.id, a_group.id}
    received_ids = {group['id'] for group in data}
    assert len(received_ids) == len(expected_ids)
    assert expected_ids.issubset(received_ids)

    # Can retrieve a specific group
    resp = client.get(f'/api/groups/{teaching_group_with_members.id}/')
    assert resp.status_code == 200


@pytest.mark.django_db
def test_school_inspector_group_access(
        school, other_school, school_inspector, teaching_group, other_school_teaching_group):
    client = APIClient()
    client.force_authenticate(user=school_inspector)

    # Can list groups in affiliated school
    resp = client.get('/api/groups/', {'school': school.id})
    assert resp.status_code == 200
    expected_ids = {teaching_group.id}
    received_ids = {group['id'] for group in resp.json()}
    assert expected_ids == received_ids

    # Will not include groups from other school
    assert other_school_teaching_group.id not in received_ids

    # Will not list groups from non-affiliated school
    resp = client.get('/api/groups/', {'school': other_school.id})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 0


@pytest.mark.django_db
def test_teacher_group_access(
    teaching_group_with_members, other_teaching_group_with_members, disabled_group, teacher, school,
        teacher_role):
    client = APIClient()
    client.force_authenticate(user=teacher)

    # School ID is required for listing groups
    resp = client.get('/api/groups/')
    assert resp.status_code == 400

    # Teacher can only list own groups
    resp = client.get('/api/groups/', {'school': school.id})
    assert resp.status_code == 200
    data = resp.json()
    expected_ids = {teaching_group_with_members.id}
    received_ids = {group['id'] for group in data}
    assert len(received_ids) == len(expected_ids)
    assert expected_ids.issubset(received_ids)

    # Teacher cannot see disabled groups even if they are a member
    disabled_group.add_member(teacher, teacher_role)
    resp = client.get('/api/groups/', {'school': school.id})
    assert resp.status_code == 200
    data = resp.json()
    received_ids = {group['id'] for group in data}
    assert disabled_group.id not in received_ids

    # Teacher can retrieve own group
    resp = client.get(f'/api/groups/{teaching_group_with_members.id}/')
    assert resp.status_code == 200

    # Teacher cannot retrieve other group
    resp = client.get(f'/api/groups/{other_teaching_group_with_members.id}/')
    assert resp.status_code == 404


@pytest.mark.django_db
def test_student_group_access(
        teaching_group_with_members, other_teaching_group_with_members, disabled_group, school, student_role):
    student = teaching_group_with_members.get_students().first()
    client = APIClient()
    client.force_authenticate(user=student)

    # School ID is required for listing groups
    resp = client.get('/api/groups/')
    assert resp.status_code == 400

    # Student can only list own groups
    resp = client.get('/api/groups/', {'school': school.id})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert all(group['id'] == teaching_group_with_members.id for group in data)

    # Add student to new groups and verify student does not see it
    a_group = Group.objects.create(
        feide_id="fc:group:other",
        display_name="Other Group",
        type="basis",
        school=school,
        is_enabled=True
    )
    a_group.add_member(student, student_role)
    resp = client.get('/api/groups/', {'school': school.id})
    data = resp.json()
    expected_ids = {teaching_group_with_members.id, a_group.id}
    received_ids = {group['id'] for group in data}
    assert len(received_ids) == len(expected_ids)
    assert expected_ids.issubset(received_ids)

    # Student cannot see disabled groups even if they are a member
    disabled_group.add_member(student, student_role)
    resp = client.get('/api/groups/', {'school': school.id})
    assert resp.status_code == 200
    data = resp.json()
    received_ids = {group['id'] for group in data}
    assert disabled_group.id not in received_ids

    # Student can retrieve own group
    resp = client.get(f'/api/groups/{teaching_group_with_members.id}/')
    assert resp.status_code == 200

    # Student cannot retrieve other group
    resp = client.get(f'/api/groups/{other_teaching_group_with_members.id}/')
    assert resp.status_code == 404


@pytest.mark.django_db
def test_group_filtering_by_user_and_role_bug(school, teacher_role, student_role):
    """
    Test that filtering groups by both user and roles correctly filters
    on the SAME membership record, not separate records.
    """
    from mastery.models import User, Group

    client = APIClient()

    # Create a teacher and student
    teacher = User.objects.create(
        name="Test Teacher",
        feide_id="test-teacher@example.com",
        email="test-teacher@example.com"
    )
    student = User.objects.create(
        name="Test Student",
        feide_id="test-student@example.com",
        email="test-student@example.com"
    )

    # Create a group with both teacher and student
    group = Group.objects.create(
        feide_id="fc:group:test",
        display_name="Test Group",
        type="basis",
        school=school,
        is_enabled=True
    )
    group.add_member(teacher, teacher_role)
    group.add_member(student, student_role)

    # Authenticate as superadmin to have full access
    superadmin = User.objects.create(
        name="Superadmin",
        feide_id="superadmin@example.com",
        email="superadmin@example.com",
        is_superadmin=True
    )
    client.force_authenticate(user=superadmin)

    resp = client.get('/api/groups/', {
        'school': school.id,
        'user': teacher.id,
        'roles': 'student'
    })
    assert resp.status_code == 200
    data = resp.json()

    assert len(data) == 0

    # Verify correct behavior: teacher should be found as teacher
    resp = client.get('/api/groups/', {
        'school': school.id,
        'user': teacher.id,
        'roles': 'teacher'
    })
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]['id'] == group.id

    # Verify correct behavior: student should be found as student
    resp = client.get('/api/groups/', {
        'school': school.id,
        'user': student.id,
        'roles': 'student'
    })
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]['id'] == group.id


@pytest.mark.django_db
def test_basis_teacher_can_access_student_groups(
        school, basis_group, teacher, student, other_student, teacher_role, student_role):
    """
    Test that teachers in basis groups can access all groups their students are members of.
    """

    # Basis group with a teacher and two students
    basis_group.add_member(teacher, teacher_role)
    basis_group.add_member(student, student_role)
    basis_group.add_member(other_student, student_role)

    # Teaching groups where the basis group students are also members
    teaching_group_1 = Group.objects.create(
        feide_id="fc:group:teaching-1",
        display_name="Math 7a",
        type="teaching",
        school=school,
        is_enabled=True
    )
    teaching_group_1.add_member(student, student_role)

    teaching_group_2 = Group.objects.create(
        feide_id="fc:group:teaching-2",
        display_name="English 7a",
        type="teaching",
        school=school,
        is_enabled=True
    )
    teaching_group_2.add_member(other_student, student_role)

    # Teaching group with both students
    teaching_group_3 = Group.objects.create(
        feide_id="fc:group:teaching-3",
        display_name="Science 7a",
        type="teaching",
        school=school,
        is_enabled=True
    )
    teaching_group_3.add_member(student, student_role)
    teaching_group_3.add_member(other_student, student_role)

    # Teaching group with a student NOT in the basis group (should not be visible)
    student_not_in_basis = User.objects.create(
        name="Student Not In Basis",
        feide_id="student-not-in-basis@example.com",
        email="student-not-in-basis@example.com"
    )
    teaching_group_not_visible = Group.objects.create(
        feide_id="fc:group:teaching-not-visible",
        display_name="Art 7a",
        type="teaching",
        school=school,
        is_enabled=True
    )
    teaching_group_not_visible.add_member(student_not_in_basis, student_role)

    # Disabled teaching group with basis students (should not be visible)
    disabled_teaching_group = Group.objects.create(
        feide_id="fc:group:teaching-disabled",
        display_name="Music 7a (disabled)",
        type="teaching",
        school=school,
        is_enabled=False
    )
    disabled_teaching_group.add_member(student, student_role)

    client = APIClient()
    client.force_authenticate(user=teacher)

    # Teacher should see:
    # 1. Their own basis group (as teacher)
    # 2. All teaching groups where their basis students are members (if enabled)
    resp = client.get('/api/groups/', {'school': school.id})
    assert resp.status_code == 200
    data = resp.json()
    received_ids = {group['id'] for group in data}

    # Expected groups: basis_group + all enabled teaching groups with basis students
    expected_ids = {basis_group.id, teaching_group_1.id, teaching_group_2.id, teaching_group_3.id}
    assert received_ids == expected_ids, f"Expected {expected_ids}, but got {received_ids}"

    # Verify the teacher can retrieve each of these groups
    for group_id in expected_ids:
        resp = client.get(f'/api/groups/{group_id}/')
        assert resp.status_code == 200

    # Verify the teacher cannot retrieve groups they shouldn't have access to
    resp = client.get(f'/api/groups/{teaching_group_not_visible.id}/')
    assert resp.status_code == 404

    resp = client.get(f'/api/groups/{disabled_teaching_group.id}/')
    assert resp.status_code == 404


@pytest.mark.django_db
def test_basis_teacher_without_students_sees_only_own_group(
        school, basis_group, teacher, teacher_role):
    """
    Test that a basis group teacher without students only sees their own basis group.
    """

    # Basis group with only a teacher (no students)
    basis_group.add_member(teacher, teacher_role)

    # Other groups that should not be visible
    other_group = Group.objects.create(
        feide_id="fc:group:other",
        display_name="Other Group",
        type="teaching",
        school=school,
        is_enabled=True
    )

    client = APIClient()
    client.force_authenticate(user=teacher)

    # Teacher should only see their own basis group
    resp = client.get('/api/groups/', {'school': school.id})
    assert resp.status_code == 200
    data = resp.json()
    received_ids = {group['id'] for group in data}

    assert received_ids == {basis_group.id}
