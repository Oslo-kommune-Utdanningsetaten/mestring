import pytest
from rest_framework.test import APIClient
from mastery.models import User, Group

@pytest.mark.django_db
def test_non_user_subject_access(school, subject_with_group, subject_without_group):
    client = APIClient()
    resp = client.get(f'/api/schools/{school.id}/subjects/')
    assert resp.status_code == 403

@pytest.mark.django_db
def test_superadmin_subject_access(superadmin, school, subject_with_group, subject_without_group):
    client = APIClient()
    client.force_authenticate(user=superadmin)

    # Can list all subjects at school
    resp = client.get(f'/api/schools/{school.id}/subjects/')
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    ids = {subject['id'] for subject in data}
    assert subject_with_group.id in ids
    assert subject_without_group.id in ids
