import pytest
from rest_framework.test import APIClient
from mastery.models import (
    School, User, Group, Role, Subject, Goal, MasterySchema,
    Observation, Status, StatusCategory, UserGroup, UserSchool,
)
from django.utils import timezone

URL_TEMPLATE = '/api/delete/school_data/{}/'


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def setup_school_data(db, school, other_school, teacher_role, student_role, admin_role):
    """Create a full set of school data for deletion tests."""
    # Users
    teacher = User.objects.create(
        name="Teacher Del", feide_id="teacher-del@example.com", email="teacher-del@example.com")
    student = User.objects.create(
        name="Student Del", feide_id="student-del@example.com", email="student-del@example.com")
    # A user that exists at BOTH schools (should NOT be deleted)
    shared_user = User.objects.create(
        name="Shared User", feide_id="shared-user@example.com", email="shared-user@example.com")
    # A user with only a school-level (UserSchool) affiliation, no group membership
    school_admin_user = User.objects.create(
        name="School Admin Del", feide_id="school-admin-del@example.com",
        email="school-admin-del@example.com")

    # Groups
    group = Group.objects.create(
        feide_id="fc:group:del-teaching-group", display_name="Del Group",
        type="teaching", school=school, is_enabled=True)
    other_school_group = Group.objects.create(
        feide_id="fc:group:other-school-group", display_name="Other Group",
        type="teaching", school=other_school, is_enabled=True)

    # UserGroups (teacher and student are only linked via groups, not user_school)
    ug_teacher = UserGroup.objects.create(user=teacher, group=group, role=teacher_role)
    ug_student = UserGroup.objects.create(user=student, group=group, role=student_role)
    ug_shared = UserGroup.objects.create(user=shared_user, group=group, role=student_role)
    # Shared user also at other school
    ug_shared_other = UserGroup.objects.create(user=shared_user, group=other_school_group, role=student_role)

    # UserSchool: only the dedicated school_admin_user has a school-level role
    us_school_admin = UserSchool.objects.create(user=school_admin_user, school=school, role=admin_role)

    # Subject owned by school
    subject = Subject.objects.create(
        display_name="School Subject", short_name="SS", owned_by_school=school)
    other_subject = Subject.objects.create(
        display_name="Other Subject", short_name="OS", owned_by_school=other_school)

    # MasterySchema
    mastery_schema = MasterySchema.objects.create(
        title="Test Schema", school=school,
        config={"levels": [{"text": "L1", "min_value": 1, "max_value": 50}]})
    other_mastery_schema = MasterySchema.objects.create(
        title="Other Schema", school=other_school,
        config={"levels": [{"text": "L1", "min_value": 1, "max_value": 50}]})

    # StatusCategory
    status_category = StatusCategory.objects.create(
        title="Halvår", name="midyear", school=school, mastery_schema=mastery_schema)
    other_status_category = StatusCategory.objects.create(
        title="Halvår", name="midyear", school=other_school, mastery_schema=other_mastery_schema)

    # Goal
    goal = Goal.objects.create(
        title="Del Goal", group=group, school=school, mastery_schema=mastery_schema)
    other_goal = Goal.objects.create(
        title="Other Goal", group=other_school_group, school=other_school)

    # Observation (linked to goal -> school)
    observation = Observation.objects.create(
        student=student, goal=goal, is_visible_to_student=True)
    other_observation = Observation.objects.create(
        student=shared_user, goal=other_goal, is_visible_to_student=True)

    # Status (linked to school via mastery_schema)
    now = timezone.now()
    status = Status.objects.create(
        student=student, subject=subject, school=school,
        mastery_schema=mastery_schema, category=status_category,
        begin_at=now, end_at=now)
    other_status = Status.objects.create(
        student=shared_user, subject=other_subject, school=other_school,
        mastery_schema=other_mastery_schema, category=other_status_category,
        begin_at=now, end_at=now)

    return {
        'school': school,
        'other_school': other_school,
        'teacher': teacher,
        'student': student,
        'shared_user': shared_user,
        'group': group,
        'other_school_group': other_school_group,
        'school_admin_user': school_admin_user,
        'ug_teacher': ug_teacher,
        'ug_student': ug_student,
        'ug_shared': ug_shared,
        'ug_shared_other': ug_shared_other,
        'us_school_admin': us_school_admin,
        'subject': subject,
        'other_subject': other_subject,
        'mastery_schema': mastery_schema,
        'other_mastery_schema': other_mastery_schema,
        'status_category': status_category,
        'other_status_category': other_status_category,
        'goal': goal,
        'other_goal': other_goal,
        'observation': observation,
        'other_observation': other_observation,
        'status': status,
        'other_status': other_status,
    }


@pytest.mark.django_db
def test_delete_school_data_requires_superadmin(client, setup_school_data):
    """Non-superadmin users cannot access this endpoint."""
    data = setup_school_data
    url = URL_TEMPLATE.format(data['school'].id)
    # Unauthenticated
    resp = client.post(url, {'types': ['goal']}, format='json')
    assert resp.status_code == 403


@pytest.mark.django_db
def test_delete_school_data_invalid_types(client, superadmin, setup_school_data):
    """Invalid types are rejected."""
    data = setup_school_data
    client.force_authenticate(user=superadmin)
    url = URL_TEMPLATE.format(data['school'].id)

    resp = client.post(url, {'types': ['invalid_type']}, format='json')
    assert resp.status_code == 400
    assert 'invalid-types' in resp.json()['error']


@pytest.mark.django_db
def test_delete_school_data_empty_types(client, superadmin, setup_school_data):
    """Empty types list is rejected."""
    data = setup_school_data
    client.force_authenticate(user=superadmin)
    url = URL_TEMPLATE.format(data['school'].id)

    resp = client.post(url, {'types': []}, format='json')
    assert resp.status_code == 400


@pytest.mark.django_db
def test_delete_school_data_school_not_found(client, superadmin, db):
    """Non-existent school returns 404."""
    client.force_authenticate(user=superadmin)
    url = URL_TEMPLATE.format('nonexistent-id')

    resp = client.post(url, {'types': ['goal']}, format='json')
    assert resp.status_code == 404


@pytest.mark.django_db
def test_delete_observations_only(client, superadmin, setup_school_data):
    """Deleting observations removes only observations linked to school's goals."""
    data = setup_school_data
    client.force_authenticate(user=superadmin)
    url = URL_TEMPLATE.format(data['school'].id)

    resp = client.post(url, {'types': ['observation']}, format='json')
    assert resp.status_code == 200
    assert resp.json()['deleted']['observation'] == 1

    # School observation is gone
    assert not Observation.objects.filter(id=data['observation'].id).exists()
    # Other school observation remains
    assert Observation.objects.filter(id=data['other_observation'].id).exists()


@pytest.mark.django_db
def test_delete_status_only(client, superadmin, setup_school_data):
    """Deleting status removes only statuses at the school."""
    data = setup_school_data
    client.force_authenticate(user=superadmin)
    url = URL_TEMPLATE.format(data['school'].id)

    resp = client.post(url, {'types': ['status']}, format='json')
    assert resp.status_code == 200
    assert resp.json()['deleted']['status'] == 1

    assert not Status.objects.filter(id=data['status'].id).exists()
    assert Status.objects.filter(id=data['other_status'].id).exists()


@pytest.mark.django_db
def test_delete_goals_only(client, superadmin, setup_school_data):
    """Deleting goals removes only goals at the school (and cascades observations)."""
    data = setup_school_data
    client.force_authenticate(user=superadmin)
    url = URL_TEMPLATE.format(data['school'].id)

    resp = client.post(url, {'types': ['goal']}, format='json')
    assert resp.status_code == 200
    assert resp.json()['deleted']['goal'] == 1

    assert not Goal.objects.filter(id=data['goal'].id).exists()
    assert Goal.objects.filter(id=data['other_goal'].id).exists()
    # Observation cascaded
    assert not Observation.objects.filter(id=data['observation'].id).exists()


@pytest.mark.django_db
def test_delete_status_category_only(client, superadmin, setup_school_data):
    """Deleting status_category removes only school's categories."""
    data = setup_school_data
    client.force_authenticate(user=superadmin)
    url = URL_TEMPLATE.format(data['school'].id)

    # Must delete status first (FK constraint from status -> category via SET_NULL won't block,
    # but let's keep the test isolated)
    resp = client.post(url, {'types': ['status_category']}, format='json')
    assert resp.status_code == 200
    assert resp.json()['deleted']['statusCategory'] == 1

    assert not StatusCategory.objects.filter(id=data['status_category'].id).exists()
    assert StatusCategory.objects.filter(id=data['other_status_category'].id).exists()


@pytest.mark.django_db
def test_delete_mastery_schema_only(client, superadmin, setup_school_data):
    """Deleting mastery_schema removes only school's schemas."""
    data = setup_school_data
    client.force_authenticate(user=superadmin)
    url = URL_TEMPLATE.format(data['school'].id)

    # Delete dependent status_category first (CASCADE from mastery_schema -> status_category)
    resp = client.post(url, {'types': ['status_category', 'mastery_schema']}, format='json')
    assert resp.status_code == 200
    assert resp.json()['deleted']['masterySchema'] == 1

    assert not MasterySchema.objects.filter(id=data['mastery_schema'].id).exists()
    assert MasterySchema.objects.filter(id=data['other_mastery_schema'].id).exists()


@pytest.mark.django_db
def test_delete_subject_only(client, superadmin, setup_school_data):
    """Deleting subject removes only school-owned subjects."""
    data = setup_school_data
    client.force_authenticate(user=superadmin)
    url = URL_TEMPLATE.format(data['school'].id)

    resp = client.post(url, {'types': ['subject']}, format='json')
    assert resp.status_code == 200
    assert resp.json()['deleted']['subject'] == 1

    assert not Subject.objects.filter(id=data['subject'].id).exists()
    assert Subject.objects.filter(id=data['other_subject'].id).exists()


@pytest.mark.django_db
def test_delete_user_group_removes_orphaned_users(client, superadmin, setup_school_data):
    """Deleting user_group removes memberships and orphaned users, but not shared users."""
    data = setup_school_data
    client.force_authenticate(user=superadmin)
    url = URL_TEMPLATE.format(data['school'].id)

    resp = client.post(url, {'types': ['user_group']}, format='json')
    assert resp.status_code == 200
    assert resp.json()['deleted']['userGroup'] == 3  # teacher, student, shared
    assert resp.json()['deleted']['user'] == 2  # teacher and student are orphaned

    # UserGroups at school are gone
    assert not UserGroup.objects.filter(group__school=data['school']).exists()
    # Other school user_groups remain
    assert UserGroup.objects.filter(id=data['ug_shared_other'].id).exists()

    # Teacher has no user_school -> orphaned and deleted
    assert not User.objects.filter(id=data['teacher'].id).exists()
    # Student has no other references -> orphaned and deleted
    assert not User.objects.filter(id=data['student'].id).exists()
    # Shared user still has user_group at other school -> NOT deleted
    assert User.objects.filter(id=data['shared_user'].id).exists()
    # school_admin_user has user_school -> NOT deleted
    assert User.objects.filter(id=data['school_admin_user'].id).exists()


@pytest.mark.django_db
def test_delete_user_school_removes_orphaned_users(client, superadmin, setup_school_data):
    """Deleting user_school removes school employment records and orphaned users."""
    data = setup_school_data
    client.force_authenticate(user=superadmin)
    url = URL_TEMPLATE.format(data['school'].id)

    resp = client.post(url, {'types': ['user_school']}, format='json')
    assert resp.status_code == 200
    assert resp.json()['deleted']['userSchool'] == 1
    assert resp.json()['deleted']['user'] == 1  # school_admin_user has no group memberships -> orphaned

    assert not UserSchool.objects.filter(school=data['school']).exists()
    # school_admin_user has no user_groups -> deleted
    assert not User.objects.filter(id=data['school_admin_user'].id).exists()
    # Teacher still has user_group -> NOT deleted
    assert User.objects.filter(id=data['teacher'].id).exists()


@pytest.mark.django_db
def test_delete_group_only(client, superadmin, setup_school_data):
    """Deleting groups removes only groups at the school."""
    data = setup_school_data
    client.force_authenticate(user=superadmin)
    url = URL_TEMPLATE.format(data['school'].id)

    # Delete goals and user_groups first to avoid FK/check constraint issues
    resp = client.post(url, {'types': ['goal', 'user_group', 'group']}, format='json')
    assert resp.status_code == 200
    assert resp.json()['deleted']['group'] == 1
    assert resp.json()['deleted']['userGroup'] == 3

    assert not Group.objects.filter(id=data['group'].id).exists()
    assert Group.objects.filter(id=data['other_school_group'].id).exists()


@pytest.mark.django_db
def test_delete_all_types(client, superadmin, setup_school_data):
    """Deleting all types removes all school data without FK errors."""
    data = setup_school_data
    client.force_authenticate(user=superadmin)
    url = URL_TEMPLATE.format(data['school'].id)

    all_types = [
        'observation', 'status', 'goal', 'status_category', 'mastery_schema',
        'subject', 'user_group', 'user_school', 'group',
    ]
    resp = client.post(url, {'types': all_types}, format='json')
    assert resp.status_code == 200

    result = resp.json()['deleted']
    assert result['observation'] == 1
    assert result['status'] == 1
    assert result['goal'] == 1
    assert result['statusCategory'] == 1
    assert result['masterySchema'] == 1
    assert result['subject'] == 1
    assert result['userGroup'] == 3
    assert result['userSchool'] == 1
    assert result['group'] == 1
    # teacher+student orphaned after user_group, school_admin_user after user_school
    assert result['user'] == 3

    # Other school data is untouched
    assert Goal.objects.filter(school=data['other_school']).count() == 1
    assert Observation.objects.filter(goal__school=data['other_school']).count() == 1
    assert Group.objects.filter(school=data['other_school']).count() == 1
    assert MasterySchema.objects.filter(school=data['other_school']).count() == 1
    assert StatusCategory.objects.filter(school=data['other_school']).count() == 1
    assert Status.objects.filter(school=data['other_school']).count() == 1
    assert Subject.objects.filter(owned_by_school=data['other_school']).count() == 1


@pytest.mark.django_db
def test_delete_respects_order_even_if_types_unordered(client, superadmin, setup_school_data):
    """Even if types are passed in wrong order, deletion respects dependency order."""
    data = setup_school_data
    client.force_authenticate(user=superadmin)
    url = URL_TEMPLATE.format(data['school'].id)

    # Pass types in reverse order - should still work
    resp = client.post(url, {'types': ['group', 'user_group', 'goal', 'observation']}, format='json')
    assert resp.status_code == 200
    result = resp.json()['deleted']
    assert result['observation'] == 1
    assert result['goal'] == 1
    assert result['userGroup'] == 3
    assert result['user'] == 2  # teacher and student orphaned after user_group deletion
    assert result['group'] == 1
