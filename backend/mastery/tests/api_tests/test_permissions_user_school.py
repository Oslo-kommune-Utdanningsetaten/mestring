import pytest
from rest_framework.test import APIClient
from mastery.models import UserSchool


@pytest.mark.django_db
def test_non_user_user_access(school):
    client = APIClient()
    # Non-authenticated user cannot access any user_school data
    resp = client.get('/api/user-schools/')
    assert resp.status_code == 403
    resp = client.get('/api/user-schools/', {'school': school.id})
    assert resp.status_code == 403


@pytest.mark.django_db
def test_superadmin_access(superadmin, school, school_admin):
    client = APIClient()
    client.force_authenticate(user=superadmin)

    # School param required
    resp = client.get('/api/user-schools/')
    assert resp.status_code == 400

    # Can list any user_school data in school
    resp = client.get('/api/user-schools/', {'school': school.id})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert any(item.get("user", {}).get("id") == school_admin.id for item in data)

    # Can retrieve specific user_school
    us = UserSchool.objects.filter(user_id=school_admin.id).first()
    resp = client.get(f'/api/user-schools/{us.id}/')
    assert resp.status_code == 200


@pytest.mark.django_db
def test_user_self_access(school, other_school, school_admin, other_school_admin):
    client = APIClient()
    client.force_authenticate(user=school_admin)

    # School param required
    resp = client.get('/api/user-schools/')
    assert resp.status_code == 400

    # Can list their own user_school data in school
    resp = client.get('/api/user-schools/', {'school': school.id})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert any(item.get("user", {}).get("id") == school_admin.id for item in data)
    # Cannot see other user_school data
    assert not any(item.get("user", {}).get("id") == other_school_admin.id for item in data)

    # Can retrieve own user_school data
    us = UserSchool.objects.filter(user_id=school_admin.id).first()
    resp = client.get(f'/api/user-schools/{us.id}/')
    assert resp.status_code == 200

    # Retrieve user_school data for other schools gives empty list
    resp = client.get('/api/user-schools/', {'school': other_school.id})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 0

    # Cannot retrieve other users user_school data
    us = UserSchool.objects.filter(user_id=other_school_admin.id).first()
    resp = client.get(f'/api/user-schools/{us.id}/')
    assert resp.status_code == 403
