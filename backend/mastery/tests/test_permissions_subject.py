import pytest
from rest_framework.test import APIClient
from mastery.models import User, Group

@pytest.mark.django_db
def test_non_user_subject_access(school, subject_with_group, subject_without_group):
    client = APIClient()
    # Non-authenticated user cannot access subjects
    resp = client.get(f'/api/schools/{school.id}/subjects/')
    assert resp.status_code == 403
    
@pytest.mark.django_db
def test_superadmin_subject_access(superadmin, school, subject_with_group, subject_without_group):
    client = APIClient()
    client.force_authenticate(user=superadmin)

    # Superadmin can list all subjects
    resp = client.get(f'/api/schools/{school.id}/subjects/')
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    ids = {subject['id'] for subject in data}
    assert subject_with_group.id in ids
    assert subject_without_group.id in ids

@pytest.mark.django_db
def test_user_subject_access(teaching_group_with_members, school, subject_with_group, subject_without_group):      
    client = APIClient()
    # Subjects are not secret
    # Any user should only see all subjects taught at their school
    teacher = teaching_group_with_members.get_teachers().first()
    student = teaching_group_with_members.get_students().first()
    for user in [teacher, student]:
        client.force_authenticate(user=user)

        resp = client.get(f'/api/schools/{school.id}/subjects/')
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        ids = {subject['id'] for subject in data}
        assert subject_with_group.id in ids
        assert subject_without_group.id in ids
