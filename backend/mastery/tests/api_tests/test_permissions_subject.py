import pytest
from datetime import datetime
from django.utils import timezone
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
    resp = client.get('/api/subjects/', {'school': school.id, 'school_year': 'all'})
    assert resp.status_code == 200
    received_ids = {s['id'] for s in resp.json()}
    expected_ids = {subject_with_group.id, subject_owned_by_school.id}
    assert received_ids == expected_ids

    # Superadmin can list subjects specifically owned by school
    resp = client.get(f'/api/subjects/', {
        'school': school.id, 'school_year': 'all', 'is_owned_by_school': True})
    assert resp.status_code == 200
    received_ids = {s['id'] for s in resp.json()}
    expected_ids = {subject_owned_by_school.id}
    assert received_ids == expected_ids

    # Superadmin can list subjects not specifically owned by school
    resp = client.get(f'/api/subjects/', {
        'school': school.id, 'school_year': 'all', 'is_owned_by_school': False})
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
        resp = client.get(f'/api/subjects/', {'school': school.id, 'school_year': 'all'})
        assert resp.status_code == 200
        expected_ids = {subject_with_group.id, subject_owned_by_school.id}
        received_ids = {subject['id'] for subject in resp.json()}
        assert received_ids == expected_ids

        # Can list subjects via groups in school
        resp = client.get(f'/api/subjects/', {
            'school': school.id, 'school_year': 'all', 'is_owned_by_school': False})
        assert resp.status_code == 200
        expected_ids = {subject_with_group.id}
        received_ids = {subject['id'] for subject in resp.json()}
        assert received_ids == expected_ids

        # Can list subjects owned by school
        resp = client.get(f'/api/subjects/', {
            'school': school.id, 'school_year': 'all', 'is_owned_by_school': True})
        assert resp.status_code == 200
        expected_ids = {subject_owned_by_school.id}
        received_ids = {subject['id'] for subject in resp.json()}
        assert received_ids == expected_ids

        # Cannot list subjects owned by other schools
        resp = client.get(f'/api/subjects/', {'school': other_school.id, 'school_year': 'all'})
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
        resp = client.get(f'/api/subjects/', {'school': other_school.id, 'school_year': 'all'})
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
    resp = client.get(f'/api/subjects/', {'school': school.id, 'school_year': 'all'})
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
def test_subject_filter_by_users(
        school, student, other_student, teacher, school_admin, student_role, teacher_role):
    """
    Test that the 'students' query parameter correctly filters subjects by:
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
    resp = client.get('/api/subjects/', {
        'school': school.id, 'school_year': 'all', 'students': student.id})
    assert resp.status_code == 200
    received_ids = {s['id'] for s in resp.json()}
    expected_ids = {subject_with_group.id, subject_with_individual_goal.id}
    assert received_ids == expected_ids

    # Test filtering by unrelated user, returns no subjects
    resp = client.get('/api/subjects/', {
        'school': school.id, 'school_year': 'all', 'students': other_student.id})
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
    resp = client.get('/api/subjects/', {
        'school': school.id, 'school_year': 'all', 'students': f'{student.id},{other_student.id}'})
    assert resp.status_code == 200
    received_ids = {s['id'] for s in resp.json()}
    expected_ids = {subject_with_group.id, subject_with_individual_goal.id, subject_unrelated.id}
    assert received_ids == expected_ids

    # Test that teacher can see subjects they're connected to via group
    resp = client.get('/api/subjects/', {
        'school': school.id, 'school_year': 'all', 'students': teacher.id})
    assert resp.status_code == 200
    received_ids = {s['id'] for s in resp.json()}
    expected_ids = {subject_with_group.id}
    assert received_ids == expected_ids

    # Test school admin filtering by multiple users
    client.force_authenticate(user=school_admin)
    resp = client.get('/api/subjects/', {
        'school': school.id, 'school_year': 'all', 'students': f'{student.id},{other_student.id}'})
    assert resp.status_code == 200
    received_ids = {s['id'] for s in resp.json()}
    expected_ids = {subject_with_group.id, subject_with_individual_goal.id, subject_unrelated.id}
    assert received_ids == expected_ids


@pytest.mark.django_db
def test_subject_school_year_filter_scopes_groups_and_goals_to_school(
        school, other_school, superadmin, student):
    subject_with_other_school_group = Subject.objects.create(
        display_name="Other-school group subject",
        short_name="Other group",
        owned_by_school=school,
    )
    subject_with_other_school_goal = Subject.objects.create(
        display_name="Other-school goal subject",
        short_name="Other goal",
        owned_by_school=school,
    )

    Group.objects.create(
        feide_id="fc:group:other-school-year-group",
        display_name="Other-school year group",
        type="teaching",
        school=other_school,
        subject=subject_with_other_school_group,
        valid_from=timezone.make_aware(datetime(2024, 9, 1)),
        valid_to=timezone.make_aware(datetime(2025, 6, 1)),
        is_enabled=True,
    )

    goal = Goal.objects.create(
        title="Other-school year goal",
        student=student,
        subject=subject_with_other_school_goal,
        school=other_school,
    )
    Goal.objects.filter(id=goal.id).update(
        created_at=timezone.make_aware(datetime(2024, 9, 1))
    )

    client = APIClient()
    client.force_authenticate(user=superadmin)
    response = client.get('/api/subjects/', {
        'school': school.id,
        'school_year': '2024-2025',
    })

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.django_db
def test_subject_student_filter_scopes_group_membership_to_school_year(
        school, superadmin, student, student_role):
    subject_with_old_membership = Subject.objects.create(
        display_name="Old membership subject",
        short_name="Old membership",
    )
    old_group = Group.objects.create(
        feide_id="fc:group:old-membership-group",
        display_name="Old membership group",
        type="teaching",
        school=school,
        subject=subject_with_old_membership,
        valid_from=timezone.make_aware(datetime(2023, 9, 1)),
        valid_to=timezone.make_aware(datetime(2024, 6, 1)),
        is_enabled=True,
    )
    old_group.add_member(student, student_role)
    Group.objects.create(
        feide_id="fc:group:current-year-unrelated-group",
        display_name="Current-year group without student",
        type="teaching",
        school=school,
        subject=subject_with_old_membership,
        valid_from=timezone.make_aware(datetime(2024, 9, 1)),
        valid_to=timezone.make_aware(datetime(2025, 6, 1)),
        is_enabled=True,
    )

    subject_with_current_membership = Subject.objects.create(
        display_name="Current membership subject",
        short_name="Current membership",
    )
    current_group = Group.objects.create(
        feide_id="fc:group:current-membership-group",
        display_name="Current membership group",
        type="teaching",
        school=school,
        subject=subject_with_current_membership,
        valid_from=timezone.make_aware(datetime(2024, 9, 1)),
        valid_to=timezone.make_aware(datetime(2025, 6, 1)),
        is_enabled=True,
    )
    current_group.add_member(student, student_role)

    client = APIClient()
    client.force_authenticate(user=superadmin)
    response = client.get('/api/subjects/', {
        'school': school.id,
        'school_year': '2024-2025',
        'students': student.id,
    })

    assert response.status_code == 200
    assert {subject['id'] for subject in response.json()} == {subject_with_current_membership.id}


@pytest.mark.django_db
def test_subject_student_filter_ignores_goals_outside_school_year(school, superadmin, student):
    subject = Subject.objects.create(
        display_name="Goal from another year",
        short_name="Other year goal",
    )
    Group.objects.create(
        feide_id="fc:group:goal-subject-previous-year-group",
        display_name="Previous-year group without student",
        type="teaching",
        school=school,
        subject=subject,
        valid_from=timezone.make_aware(datetime(2024, 9, 1)),
        valid_to=timezone.make_aware(datetime(2025, 6, 1)),
        is_enabled=True,
    )
    goal = Goal.objects.create(
        title="Student goal from following year",
        student=student,
        subject=subject,
        school=school,
    )
    Goal.objects.filter(id=goal.id).update(
        created_at=timezone.make_aware(datetime(2025, 9, 1))
    )

    client = APIClient()
    client.force_authenticate(user=superadmin)
    response = client.get('/api/subjects/', {
        'school': school.id,
        'school_year': '2024-2025',
        'students': student.id,
    })

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.django_db
def test_subject_student_filter_uses_feide_utc_school_year_boundaries(
        school, superadmin, student, student_role):
    subject = Subject.objects.create(
        display_name="School year boundary subject",
        short_name="Boundary",
    )
    group = Group.objects.create(
        feide_id="fc:group:school-year-boundary",
        display_name="School year boundary group",
        type="teaching",
        school=school,
        subject=subject,
        valid_from=datetime.fromisoformat("2026-07-31T22:00:00+00:00"),
        valid_to=datetime.fromisoformat("2027-07-31T22:00:00+00:00"),
        is_enabled=True,
    )
    group.add_member(student, student_role)
    Group.objects.create(
        feide_id="fc:group:school-year-boundary-previous-bridge",
        display_name="Previous-year group for current subject",
        type="teaching",
        school=school,
        subject=subject,
        valid_from=datetime.fromisoformat("2025-07-31T22:00:00+00:00"),
        valid_to=datetime.fromisoformat("2026-07-31T22:00:00+00:00"),
        is_enabled=True,
    )

    previous_subject = Subject.objects.create(
        display_name="Previous school year subject",
        short_name="Previous year",
    )
    previous_group = Group.objects.create(
        feide_id="fc:group:previous-school-year-boundary",
        display_name="Previous school year group",
        type="teaching",
        school=school,
        subject=previous_subject,
        valid_from=datetime.fromisoformat("2025-07-31T22:00:00+00:00"),
        valid_to=datetime.fromisoformat("2026-07-31T22:00:00+00:00"),
        is_enabled=True,
    )
    previous_group.add_member(student, student_role)
    Group.objects.create(
        feide_id="fc:group:previous-school-year-boundary-current-bridge",
        display_name="Current-year group for previous subject",
        type="teaching",
        school=school,
        subject=previous_subject,
        valid_from=datetime.fromisoformat("2026-07-31T22:00:00+00:00"),
        valid_to=datetime.fromisoformat("2027-07-31T22:00:00+00:00"),
        is_enabled=True,
    )

    client = APIClient()
    client.force_authenticate(user=superadmin)
    previous_year_response = client.get('/api/subjects/', {
        'school': school.id,
        'school_year': '2025-2026',
        'students': student.id,
    })
    current_year_response = client.get('/api/subjects/', {
        'school': school.id,
        'school_year': '2026-2027',
        'students': student.id,
    })

    assert previous_year_response.status_code == 200
    assert {item['id'] for item in previous_year_response.json()} == {previous_subject.id}
    assert current_year_response.status_code == 200
    assert {item['id'] for item in current_year_response.json()} == {subject.id}


@pytest.mark.django_db
def test_subject_school_year_filter_uses_half_open_utc_ranges(
        school, superadmin, student, student_role):
    year_start = datetime.fromisoformat("2026-07-31T22:00:00+00:00")
    year_end = datetime.fromisoformat("2027-07-31T22:00:00+00:00")
    included_group_subject = Subject.objects.create(
        display_name="Group valid in school year",
        short_name="Group in range",
    )
    included_group = Group.objects.create(
        feide_id="fc:group:half-open-included",
        display_name="Group spanning school year",
        type="teaching",
        school=school,
        subject=included_group_subject,
        valid_from=year_start,
        valid_to=year_end,
        is_enabled=True,
    )
    included_group.add_member(student, student_role)

    group_ending_at_start_subject = Subject.objects.create(
        display_name="Group ending at school year start",
        short_name="Ends at start",
    )
    Group.objects.create(
        feide_id="fc:group:half-open-ends-at-start",
        display_name="Group ending at boundary",
        type="teaching",
        school=school,
        subject=group_ending_at_start_subject,
        valid_from=datetime.fromisoformat("2025-07-31T22:00:00+00:00"),
        valid_to=year_start,
        is_enabled=True,
    )

    group_starting_at_end_subject = Subject.objects.create(
        display_name="Group starting at school year end",
        short_name="Starts at end",
    )
    Group.objects.create(
        feide_id="fc:group:half-open-starts-at-end",
        display_name="Group starting at boundary",
        type="teaching",
        school=school,
        subject=group_starting_at_end_subject,
        valid_from=year_end,
        valid_to=datetime.fromisoformat("2028-07-31T22:00:00+00:00"),
        is_enabled=True,
    )

    goal_at_start_subject = Subject.objects.create(
        display_name="Goal created at school year start",
        short_name="Goal at start",
    )
    goal_at_start = Goal.objects.create(
        title="Goal at school-year start",
        student=student,
        subject=goal_at_start_subject,
        school=school,
    )
    Goal.objects.filter(id=goal_at_start.id).update(created_at=year_start)

    goal_at_end_subject = Subject.objects.create(
        display_name="Goal created at school year end",
        short_name="Goal at end",
    )
    goal_at_end = Goal.objects.create(
        title="Goal at school-year end",
        student=student,
        subject=goal_at_end_subject,
        school=school,
    )
    Goal.objects.filter(id=goal_at_end.id).update(created_at=year_end)

    client = APIClient()
    client.force_authenticate(user=superadmin)
    response = client.get('/api/subjects/', {
        'school': school.id,
        'school_year': '2026-2027',
        'students': student.id,
    })

    assert response.status_code == 200
    assert {item['id'] for item in response.json()} == {
        included_group_subject.id,
        goal_at_start_subject.id,
    }
