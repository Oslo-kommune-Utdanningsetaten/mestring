import pytest
from rest_framework.test import APIClient
from mastery.models import User, Group, Subject, Goal


@pytest.mark.django_db
def test_non_user_subject_access(school, subject_with_group, subject_without_group):
    client = APIClient()
    # Non-authenticated user cannot access subjects
    resp = client.get(f'/api/subjects/')
    assert resp.status_code == 403
    resp = client.get(f'/api/subjects/', {'school': school.id})
    assert resp.status_code == 403
    resp = client.get(f'/api/subjects/', {'owned_by': school.id})
    assert resp.status_code == 403
    resp = client.get(f'/api/subjects/{subject_with_group.id}/')
    assert resp.status_code == 403
    resp = client.get(f'/api/subjects/{subject_without_group.id}/')
    assert resp.status_code == 403


@pytest.mark.django_db
def test_superadmin_subject_access(superadmin, school, subject_with_group, subject_without_group):
    client = APIClient()
    client.force_authenticate(user=superadmin)

    # school or owned_by params are needed, even for Superadmin
    resp = client.get(f'/api/subjects/')
    assert resp.status_code == 400

    # Superadmin can list both kinds of subjects in one go
    resp = client.get('/api/subjects/', {'school': school.id})
    data = resp.json()
    expected_ids = {subject_without_group.id, subject_with_group.id}
    received_ids = {group['id'] for group in data}
    assert len(received_ids) == len(expected_ids)
    assert expected_ids.issubset(received_ids)

    # Superadmin can list subjects not specifically owned by school
    resp = client.get(f'/api/subjects/', {'school': school.id, 'is_owned_by_school': False})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    ids = {subject['id'] for subject in data}
    assert subject_with_group.id in ids
    assert subject_without_group.id not in ids

    # Superadmin can list all subjects owned by school
    resp = client.get(f'/api/subjects/', {'school': school.id, 'is_owned_by_school': True})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    ids = {subject['id'] for subject in data}
    assert subject_without_group.id in ids
    assert subject_with_group.id not in ids

    # Superadmin can retrieve both kinds of subjects
    resp = client.get(f'/api/subjects/{subject_with_group.id}/')
    assert resp.status_code == 200
    resp = client.get(f'/api/subjects/{subject_without_group.id}/')
    assert resp.status_code == 200


@pytest.mark.django_db
def test_school_admin_subject_access(
        school, other_school, school_admin, subject_with_group, subject_without_group,
        subject_without_group_at_other_school):
    client = APIClient()
    client.force_authenticate(user=school_admin)

    # School admin cannot list subjects across schools
    resp = client.get(f'/api/subjects/')
    assert resp.status_code == 400

    # Can list all subjects in school
    resp = client.get(f'/api/subjects/', {'school': school.id})
    assert resp.status_code == 200
    data = resp.json()
    expected_ids = {subject_with_group.id, subject_without_group.id}
    received_ids = {group['id'] for group in data}
    assert len(received_ids) == len(expected_ids)
    assert expected_ids.issubset(received_ids)

    # Can list subjects via groups in school
    resp = client.get(f'/api/subjects/', {'school': school.id, 'is_owned_by_school': False})
    assert resp.status_code == 200
    data = resp.json()
    expected_ids = {subject_with_group.id}
    received_ids = {group['id'] for group in data}
    assert len(received_ids) == len(expected_ids)
    assert expected_ids.issubset(received_ids)
    # Will not include subjects without groups (but still owned by school)
    assert subject_without_group.id not in received_ids

    # Can list subjects owned by school
    resp = client.get(f'/api/subjects/', {'school': school.id, 'is_owned_by_school': True})
    assert resp.status_code == 200
    data = resp.json()
    expected_ids = {subject_without_group.id}
    received_ids = {group['id'] for group in data}
    assert len(received_ids) == len(expected_ids)
    assert expected_ids.issubset(received_ids)
    # Will not include subjects with groups (but still owned by school)
    assert subject_with_group.id not in received_ids

    # Cannot list subjects in other school
    resp = client.get(f'/api/subjects/', {'school': other_school.id})
    assert resp.status_code == 200
    data = resp.json()
    expected_ids = {}
    received_ids = {group['id'] for group in data}
    assert len(received_ids) == len(expected_ids)
    # Will not include subjects with groups (but still owned by school)
    assert subject_without_group_at_other_school.id not in received_ids


@pytest.mark.django_db
def test_student_subject_access(school, subject_with_group, subject_without_group):
    student = subject_with_group.groups.all()[0].get_students().first()
    client = APIClient()
    client.force_authenticate(user=student)

    # Student cannot list all subjects
    resp = client.get(f'/api/subjects/')
    assert resp.status_code == 400

    # Student can list subjects via group membership in school
    resp = client.get('/api/subjects/', {'school': school.id})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]['id'] == subject_with_group.id

    # Student can retrieve subject via group membership
    resp = client.get(f'/api/subjects/{subject_with_group.id}/')
    assert resp.status_code == 200

    # Student cannot retrieve subject with no group access
    resp = client.get(f'/api/subjects/{subject_without_group.id}/')
    assert resp.status_code == 403

    # Student can retrieve the subject if attached goal is owned
    Goal.objects.create(
        subject=subject_without_group,
        student=student,
    )
    resp = client.get(f'/api/subjects/{subject_without_group.id}/')
    assert resp.status_code == 200


@pytest.mark.django_db
def test_teacher_subject_access(
        school, student_role, teacher_role, subject_with_group, subject_without_group):
    teacher = subject_with_group.groups.all()[0].get_teachers().first()
    client = APIClient()
    client.force_authenticate(user=teacher)

    # Teacher cannot list all subjects
    resp = client.get(f'/api/subjects/')
    assert resp.status_code == 400

    # Teacher can list subjects via group membership in school
    resp = client.get('/api/subjects/', {'school': school.id})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]['id'] == subject_with_group.id

    # Teacher can retrieve subject via group membership
    resp = client.get(f'/api/subjects/{subject_with_group.id}/')
    assert resp.status_code == 200

    # Teacher can retrieve subject with no group access if they created it
    created_subject = Subject.objects.create(
        display_name="Teacher's Subject",
        created_by=teacher
    )
    resp = client.get(f'/api/subjects/{created_subject.id}/')
    assert resp.status_code == 200

    # Teacher cannot retrieve subject with no group access
    resp = client.get(f'/api/subjects/{subject_without_group.id}/')
    assert resp.status_code == 403

    # Teacher can retrieve subject if they created the attached goal
    random_student = User.objects.create(
        name="Random student",
        feide_id="asdf"
    )
    Goal.objects.create(
        student=random_student,
        subject=subject_without_group,
        created_by=teacher
    )
    resp = client.get(f'/api/subjects/{subject_without_group.id}/')
    assert resp.status_code == 200

    # Teacher can retrieve subject if the goal student is in a basis group taught by them
    a_student = User.objects.create(
        name="A student",
        feide_id="asdfasdf"
    )
    basis_group = Group.objects.create(
        feide_id="fc:group:some-basis-group",
        display_name="7a",
        type="basis",
        school=school,
        is_enabled=True
    )
    basis_group.add_member(a_student, student_role)
    basis_group.add_member(teacher, teacher_role)
    special_subject = Subject.objects.create(
        display_name="Special Subject",
        owned_by_school=school,
    )
    resp = client.get(f'/api/subjects/{special_subject.id}/')
    assert resp.status_code == 403
    Goal.objects.create(
        student=a_student,
        subject=special_subject,
    )
    resp = client.get(f'/api/subjects/{special_subject.id}/')
    assert resp.status_code == 200

    # Teacher can now list all 3 subjects
    resp = client.get('/api/subjects/', {'school': school.id})
    assert resp.status_code == 200
    data = resp.json()
    expected_ids = {special_subject.id,
                    subject_without_group.id, subject_with_group.id}
    received_ids = {group['id'] for group in data}
    assert len(received_ids) == len(expected_ids)
    assert expected_ids.issubset(received_ids)
