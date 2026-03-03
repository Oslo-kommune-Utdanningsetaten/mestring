import pytest
from rest_framework.test import APIClient
from mastery.models import UserGroup


@pytest.mark.django_db
def test_non_user_user_access(school):
    client = APIClient()
    # Non-authenticated user cannot access any user_school data
    resp = client.get('/api/user-groups/')
    assert resp.status_code == 403
    resp = client.get('/api/user-groups/', {'school': school.id})
    assert resp.status_code == 403


@pytest.mark.django_db
def test_superadmin_access(superadmin, school, other_school, teaching_group_with_members,
                           other_school_teaching_group_with_members):
    client = APIClient()
    client.force_authenticate(user=superadmin)

    # School param required
    resp = client.get('/api/user-groups/')
    assert resp.status_code == 400

    # Can list any user_groups data in school
    resp = client.get('/api/user-groups/', {'school': school.id})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == teaching_group_with_members.members.count()

    # Can list any user_groups data in school
    resp = client.get('/api/user-groups/', {'school': other_school.id})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == other_school_teaching_group_with_members.members.count()

    # Can retrieve specific user_school
    ug = UserGroup.objects.filter().first()
    resp = client.get(f'/api/user-groups/{ug.id}/')
    assert resp.status_code == 200


@pytest.mark.django_db
def test_school_admin_inspector_access(
        school, other_school, school_admin, school_inspector, teaching_group_with_members,
        other_school_teaching_group_with_members):
    client = APIClient()
    for user in [school_admin, school_inspector]:
        client.force_authenticate(user=user)

        # School param required
        resp = client.get('/api/user-groups/')
        assert resp.status_code == 400

        # Can list any user_groups data in school
        resp = client.get('/api/user-groups/', {'school': school.id})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == teaching_group_with_members.members.count()

        # Can retrieve specific user_group in school
        ug = UserGroup.objects.filter(group__school_id=school.id).first()
        resp = client.get(f'/api/user-groups/{ug.id}/')
        assert resp.status_code == 200

        # Cannot list user_group data for other school
        resp = client.get('/api/user-groups/', {'school': other_school.id})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) < other_school_teaching_group_with_members.members.count()
        assert len(data) == 0

        # Cannot retrieve specific user_group for other school
        ug = UserGroup.objects.filter(group__school_id=other_school.id).first()
        resp = client.get(f'/api/user-groups/{ug.id}/')
        assert resp.status_code == 404


@pytest.mark.django_db
def test_user_self_access(school, teacher, student, teaching_group_with_members):
    client = APIClient()
    # Log in teacher
    client.force_authenticate(user=teacher)

    # Teacher can list their own user_group data in school
    resp = client.get('/api/user-groups/', {'school': school.id})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1

    # Teacher can retrieve specific own user_group
    teacher_ug = UserGroup.objects.filter(user=teacher, group__school=school).first()
    resp = client.get(f'/api/user-groups/{teacher_ug.id}/')
    assert resp.status_code == 200
    data = resp.json()
    assert data['id'] == teacher_ug.id

    # Teacher cannot retrieve other user_group
    student_ug = UserGroup.objects.filter(user=student, group__school=school).first()
    resp = client.get(f'/api/user-groups/{student_ug.id}/')
    assert resp.status_code == 404

    # Log in student
    client.force_authenticate(user=student)

    # Student can list their own user_group data in school
    resp = client.get('/api/user-groups/', {'school': school.id})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1

    # Student can retrieve specific own user_group
    resp = client.get(f'/api/user-groups/{student_ug.id}/')
    assert resp.status_code == 200
    data = resp.json()
    assert data['id'] == student_ug.id

    # Student cannot retrieve other user_group
    resp = client.get(f'/api/user-groups/{teacher_ug.id}/')
    assert resp.status_code == 404
