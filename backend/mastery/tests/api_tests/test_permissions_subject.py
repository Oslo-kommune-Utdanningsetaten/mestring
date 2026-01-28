import pytest
from rest_framework.test import APIClient
from mastery.models import User, Group, Subject, Goal


@pytest.mark.django_db
def test_non_user_subject_access(school, subject_with_group, subject_owned_by_school):
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
    resp = client.get(f'/api/subjects/{subject_owned_by_school.id}/')
    assert resp.status_code == 403


@pytest.mark.django_db
def test_superadmin_subject_access(
        school, other_school, superadmin, subject_with_group, subject_owned_by_school,
        subject_owned_by_other_school):
    client = APIClient()
    client.force_authenticate(user=superadmin)

    # school or owned_by params are needed, even for Superadmin
    resp = client.get(f'/api/subjects/')
    assert resp.status_code == 400

    # Superadmin can list both kinds of subjects in one go
    resp = client.get('/api/subjects/', {'school': school.id})
    assert resp.status_code == 200
    received_ids = {s['id'] for s in resp.json()}
    expected_ids = {subject_with_group.id, subject_owned_by_school.id}
    assert received_ids == expected_ids

    # Superadmin can list subjects specifically owned by school
    resp = client.get(f'/api/subjects/', {'school': school.id, 'is_owned_by_school': True})
    assert resp.status_code == 200
    received_ids = {s['id'] for s in resp.json()}
    expected_ids = {subject_owned_by_school.id}
    assert received_ids == expected_ids

    # Superadmin can list subjects not specifically owned by school
    resp = client.get(f'/api/subjects/', {'school': school.id, 'is_owned_by_school': False})
    assert resp.status_code == 200
    received_ids = {s['id'] for s in resp.json()}
    expected_ids = {subject_with_group.id}
    assert received_ids == expected_ids

    # Superadmin can retrieve both kinds of subjects
    resp = client.get(f'/api/subjects/{subject_with_group.id}/')
    assert resp.status_code == 200
    resp = client.get(f'/api/subjects/{subject_owned_by_school.id}/')
    assert resp.status_code == 200

    # Can create a subject owned by another school
    payload = {
        'display_name': 'Nytt fag',
        'short_name': 'Fag',
        'grep_code': 'g1',
        'grep_group_code': 'gg1',
        'owned_by_school_id': other_school.id,
    }
    resp = client.post('/api/subjects/', payload, format='json')
    assert resp.status_code == 201
    created = resp.json()
    created_id = created.get('id')
    assert created_id is not None

    # Can edit the created subject
    resp = client.patch(f'/api/subjects/{created_id}/', {'display_name': 'Endret fag'}, format='json')
    assert resp.status_code == 200


@pytest.mark.django_db
def test_authenticated_subject_access(
        school, other_school, school_inspector, teacher, student, subject_with_group, subject_owned_by_school,
        subject_owned_by_other_school):
    client = APIClient()

    for index, user in enumerate([school_inspector, teacher, student]):
        client.force_authenticate(user=user)
        # School param is required
        resp = client.get(f'/api/subjects/')
        assert resp.status_code == 400

        # Can list all subjects in school
        resp = client.get(f'/api/subjects/', {'school': school.id})
        assert resp.status_code == 200
        expected_ids = {subject_with_group.id, subject_owned_by_school.id}
        received_ids = {subject['id'] for subject in resp.json()}
        assert received_ids == expected_ids

        # Can list subjects via groups in school
        resp = client.get(f'/api/subjects/', {'school': school.id, 'is_owned_by_school': False})
        assert resp.status_code == 200
        expected_ids = {subject_with_group.id}
        received_ids = {subject['id'] for subject in resp.json()}
        assert received_ids == expected_ids

        # Can list subjects owned by school
        resp = client.get(f'/api/subjects/', {'school': school.id, 'is_owned_by_school': True})
        assert resp.status_code == 200
        expected_ids = {subject_owned_by_school.id}
        received_ids = {subject['id'] for subject in resp.json()}
        assert received_ids == expected_ids

        # Cannot list subjects owned by other schools
        resp = client.get(f'/api/subjects/', {'school': other_school.id})
        assert resp.status_code == 200
        assert resp.json() == []

        # Cannot retrieve subjects owned by other schools
        resp = client.get(f'/api/subjects/{subject_owned_by_other_school.id}/')
        assert resp.status_code == 404

        # Cannot list or retrieve subjects which only belong to groups at other schools
        other_school_group_subject = Subject.objects.create(
            display_name="Engelsk 7. årstrinn",
            short_name="Engelsk",
            grep_code="zip",
            grep_group_code="zap",
            owned_by_school=None,
        )
        Group.objects.create(
            feide_id="fc:group:other-school-teaching-group-{index}".format(index=index),
            display_name="Some Group",
            type="teaching",
            school=other_school,
            subject=other_school_group_subject,
            is_enabled=True
        )
        resp = client.get(f'/api/subjects/', {'school': other_school.id})
        assert resp.status_code == 200
        assert resp.json() == []
        resp = client.get(f'/api/subjects/{other_school_group_subject.id}/')
        assert resp.status_code == 404


@pytest.mark.django_db
def test_school_admin_subject_access(school_admin, school, other_school, client, subject_with_group):
    client = APIClient()
    client.force_authenticate(user=school_admin)

    # School param is required for listing
    resp = client.get(f'/api/subjects/')
    assert resp.status_code == 400

    # Can list subjects for their school
    resp = client.get(f'/api/subjects/', {'school': school.id})
    assert resp.status_code == 200

    # Create a subject owned by the admin's school
    payload = {
        'display_name': 'Administrert fag',
        'short_name': 'AdmFag',
        'grep_code': 'adm1',
        'grep_group_code': 'admg1',
        'owned_by_school_id': school.id,
    }
    resp = client.post('/api/subjects/', payload, format='json')
    assert resp.status_code == 201
    created = resp.json()
    created_id = created.get('id')
    assert created_id is not None

    # Can retrieve the created subject
    resp = client.get(f'/api/subjects/{created_id}/')
    assert resp.status_code == 200

    # Can edit the created subject
    resp = client.patch(f'/api/subjects/{created_id}/', {'display_name': 'Endret av admin'}, format='json')
    assert resp.status_code == 200
    assert resp.json().get('displayName') == 'Endret av admin'

    # Can delete the created subject
    resp = client.delete(f'/api/subjects/{created_id}/')
    assert resp.status_code == 204

    # Cannot edit a subject attached to a group at the school
    resp = client.patch(f'/api/subjects/{subject_with_group.id}/',
                        {'display_name': 'Patched!'}, format='json')
    assert resp.status_code == 403

    # Cannot create a subject owned by other school
    payload = {
        'display_name': 'Administrert fag',
        'short_name': 'AdmFag',
        'grep_code': 'adm1',
        'grep_group_code': 'admg1',
        'owned_by_school': other_school.id,
    }
    resp = client.post('/api/subjects/', payload, format='json')
    assert resp.status_code == 403


@pytest.mark.django_db
def test_subject_filter_by_users(school, student, other_student, teacher, student_role, teacher_role):
    """
    Test that the 'users' query parameter correctly filters subjects by:
    1. Users who are members of groups connected to the subject
    2. Users who have individual goals connected to the subject
    """
    # Create subjects
    subject_with_group = Subject.objects.create(
        display_name="Math",
        short_name="Math",
        grep_code="math1",
        grep_group_code="mathg1",
    )

    subject_with_individual_goal = Subject.objects.create(
        display_name="Norwegian",
        short_name="Norsk",
        grep_code="nor1",
        grep_group_code="norg1",
    )

    subject_unrelated = Subject.objects.create(
        display_name="English",
        short_name="Eng",
        grep_code="eng1",
        grep_group_code="engg1",
    )

    # Create a group with student as member, connected to subject_with_group
    teaching_group = Group.objects.create(
        feide_id="fc:group:teaching-math",
        display_name="Math Group",
        type="teaching",
        school=school,
        subject=subject_with_group,
        is_enabled=True
    )
    teaching_group.add_member(student, student_role)
    teaching_group.add_member(teacher, teacher_role)

    # Create a individual goal for student connected to subject_with_individual_goal
    Goal.objects.create(
        title="Individual Norwegian Goal",
        description="Improve Norwegian skills",
        student=student,
        subject=subject_with_individual_goal,
        school=school,
    )

    client = APIClient()
    client.force_authenticate(user=teacher)

    # Test filtering by single user, returns both subjects: one via group membership, one via individual goal
    resp = client.get('/api/subjects/', {'school': school.id, 'students': student.id})
    assert resp.status_code == 200
    received_ids = {s['id'] for s in resp.json()}
    expected_ids = {subject_with_group.id, subject_with_individual_goal.id}
    assert received_ids == expected_ids

    # Test filtering by unrelated user, returns no subjects
    resp = client.get('/api/subjects/', {'school': school.id, 'students': other_student.id})
    assert resp.status_code == 200
    assert resp.json() == []

    # Create a individual goal for other_student
    Goal.objects.create(
        title="Other Student English Goal",
        description="Improve English skills",
        student=other_student,
        subject=subject_unrelated,
        school=school,
    )

    # Test filtering by multiple users, returns subjects connected to either user
    resp = client.get('/api/subjects/', {'school': school.id, 'students': f'{student.id},{other_student.id}'})
    assert resp.status_code == 200
    received_ids = {s['id'] for s in resp.json()}
    expected_ids = {subject_with_group.id, subject_with_individual_goal.id, subject_unrelated.id}
    assert received_ids == expected_ids

    # Test that teacher can see subjects they're connected to via group
    resp = client.get('/api/subjects/', {'school': school.id, 'students': teacher.id})
    assert resp.status_code == 200
    received_ids = {s['id'] for s in resp.json()}
    expected_ids = {subject_with_group.id}
    assert received_ids == expected_ids
