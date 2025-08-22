import pytest
from rest_framework.test import APIClient
from mastery.models import User, Group, Subject, Goal

# This test suite should cover all cases where users access subjects, no matter which endpoint is used

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

    # Superadmin can list all group school subjects
    resp = client.get(f'/api/subjects/', {'school': school.id})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    ids = {subject['id'] for subject in data}
    assert subject_with_group.id in ids
    assert subject_without_group.id not in ids

    # Superadmin can list all subjects owned by school
    resp = client.get(f'/api/subjects/', {'owned_by': school.id})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    ids = {subject['id'] for subject in data}
    assert subject_without_group.id in ids
    assert subject_with_group.id not in ids

    # Superadmin can retrieve both kinds of subjects in one go
    resp = client.get('/api/subjects/', {'school': school.id, 'owned_by': school.id})
    data = resp.json()
    expected_ids = {subject_without_group.id, subject_with_group.id}
    received_ids = {group['id'] for group in data}
    assert len(received_ids) == len(expected_ids)
    assert expected_ids.issubset(received_ids)

    # Superadmin can retrieve both kinds of subjects
    resp = client.get(f'/api/subjects/{subject_with_group.id}/')
    assert resp.status_code == 200
    resp = client.get(f'/api/subjects/{subject_without_group.id}/')
    assert resp.status_code == 200


@pytest.mark.django_db
def test_student_subject_access(school, subject_with_group, subject_without_group):      
    student = subject_with_group.groups.all()[0].get_students().first()
    client = APIClient()
    client.force_authenticate(user=student)

    # Student cannot list all subjects
    resp = client.get(f'/api/subjects/')
    assert resp.status_code == 400

    # Student can access subject via group membership
    resp = client.get(f'/api/subjects/{subject_with_group.id}/')
    assert resp.status_code == 200
    resp = client.get('/api/subjects/', {'school': school.id})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]['id'] == subject_with_group.id

    # Student cannot access subject with no group access
    resp = client.get(f'/api/subjects/{subject_without_group.id}/')
    assert resp.status_code == 403

    # Student can access the subject if attached goal is owned
    Goal.objects.create(
        subject=subject_without_group,
        student=student,
    )
    resp = client.get(f'/api/subjects/{subject_without_group.id}/')
    assert resp.status_code == 200

@pytest.mark.django_db
def test_teacher_subject_access(school, roles, subject_with_group, subject_without_group):      
    teacher = subject_with_group.groups.all()[0].get_teachers().first()
    client = APIClient()
    client.force_authenticate(user=teacher)

    # Teacher cannot list all subjects
    resp = client.get(f'/api/subjects/')
    assert resp.status_code == 400

    # Teacher can access subject via group membership
    resp = client.get(f'/api/subjects/{subject_with_group.id}/')
    assert resp.status_code == 200
    resp = client.get('/api/subjects/', {'school': school.id})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]['id'] == subject_with_group.id

    # Teacher can access subject with no group access if they created it
    created_subject = Subject.objects.create(
        display_name="Teacher's Subject",
        created_by=teacher
    )
    resp = client.get(f'/api/subjects/{created_subject.id}/')
    assert resp.status_code == 200

    # Teacher cannot access subject with no group access
    resp = client.get(f'/api/subjects/{subject_without_group.id}/')
    assert resp.status_code == 403

    # Teacher can access subject if they created the attached goal
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

    # Teacher can access subject if the goal student is in a basis group taught by them
    student_role, teacher_role = roles
    a_student = User.objects.create(
        name="A student",
        feide_id="asdfasdf"
    )
    basis_group = Group.objects.create(
        feide_id="fc:group:some-basis-group",
        display_name="7a",
        type="basis",
        school=school
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
    resp = client.get('/api/subjects/', {'school': school.id, 'owned_by': school.id})
    assert resp.status_code == 200
    data = resp.json()
    expected_ids = {special_subject.id, subject_without_group.id, subject_with_group.id}
    received_ids = {group['id'] for group in data}
    assert len(received_ids) == len(expected_ids)
    assert expected_ids.issubset(received_ids)