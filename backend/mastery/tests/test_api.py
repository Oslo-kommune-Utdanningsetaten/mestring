import pytest
from rest_framework.test import force_authenticate
from rest_framework.test import APIClient


@pytest.fixture
def set_up_database(db):
    print("Setting up database")


@pytest.mark.django_db
def test_schools_endpoint(school):
    """Test /schools endpoint returns school array"""
    response = APIClient().get('/api/schools/')
    assert response.status_code == 200
    assert response.json()[0]['displayName'] == school.display_name


@pytest.mark.django_db
def test_groups_endpoint_denies_unauthenticated_user(teaching_group_with_members):
    """Test /groups endpoint denies access for unauthenticated users"""
    client = APIClient()
    response = client.get('/api/groups/')
    assert response.status_code == 403

