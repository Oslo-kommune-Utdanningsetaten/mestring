import pytest
from rest_framework.test import APIClient
from mastery.models import User, Group

@pytest.mark.django_db
def test_superadmin_group_access(teaching_group_with_members, teaching_group_with_no_members, superadmin, school):
    client = APIClient()
    client.force_authenticate(user=superadmin)

    # Can list groups (should include at least the fixture group)
    resp = client.get('/api/groups/')
    assert resp.status_code == 200
    assert any(group['id'] == teaching_group_with_members.id for group in resp.json())

    # Create another group and verify superadmin sees it too
    other = Group.objects.create(
        feide_id="fc:group:other",
        display_name="Other Group",
        type="basis",
        school=school
    )
    # Group listing should include both groups
    resp = client.get('/api/groups/')
    assert resp.status_code == 200
    ids = {group['id'] for group in resp.json()}
    assert teaching_group_with_members.id in ids
    assert other.id in ids
    assert teaching_group_with_no_members.id in ids

    # Can retrieve a group
    resp = client.get(f'/api/groups/{teaching_group_with_members.id}/')
    assert resp.status_code == 200

    # Can retrieve a memberless group
    resp = client.get(f'/api/groups/{teaching_group_with_no_members.id}/')
    assert resp.status_code == 200

@pytest.mark.django_db
def test_teacher_group_access(teaching_group_with_members, teaching_group_with_no_members, roles, school):
    client = APIClient()
    teacher = teaching_group_with_members.get_teachers().first()
    client.force_authenticate(user=teacher)

    # List shows only own groups
    resp = client.get('/api/groups/')
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert all(group['id'] == teaching_group_with_members.id for group in data)

    # Create another group taught by someone else
    other_group = Group.objects.create(
        feide_id="fc:group:other-teaching-group",
        display_name="Some Group",
        type="teaching",
        school=school
    )
    # Different teacher for the other group
    other_teacher = User.objects.create(
        name="Teacher 2",
        feide_id="teacher2@example.com",
        email="teacher2@example.com"
    )
    _, teacher_role = roles
    other_group.add_member(other_teacher, teacher_role)

    # Teacher should only see their own groups in list
    resp = client.get('/api/groups/')
    assert resp.status_code == 200
    ids = {group['id'] for group in resp.json()}
    assert teaching_group_with_members.id in ids
    assert other_group.id not in ids

    # Retrieving other group should not be found
    resp = client.get(f'/api/groups/{other_group.id}/')
    assert resp.status_code == 404

@pytest.mark.django_db
def test_student_group_access(teaching_group_with_members, teaching_group_with_no_members):
    client = APIClient()
    student = teaching_group_with_members.get_students().first()
    client.force_authenticate(user=student)

    # List group with membership is allowed
    resp = client.get('/api/groups/')
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert all(group['id'] == teaching_group_with_members.id for group in data)

    # Retrieve should also be allowed
    resp = client.get(f'/api/groups/{teaching_group_with_members.id}/')
    assert resp.status_code == 200

    # Retrieve other group should be forbidden
    resp = client.get(f'/api/groups/{teaching_group_with_no_members.id}/')
    assert resp.status_code == 404
