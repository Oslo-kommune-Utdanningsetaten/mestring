import pytest
from django.test import RequestFactory
from rest_framework.test import force_authenticate
from mastery.models import School, UserGroup
from mastery.views import SchoolViewSet
from rest_framework.test import APIClient


@pytest.fixture
def set_up_database(db):
    print("Setting up database")


@pytest.mark.django_db
def test_schools_endpoint(school):
    """Test /schools endpoint returns school array"""
    response = APIClient().get('/schools/')
    assert response.status_code == 200
    assert response.json()[0]['displayName'] == school.display_name

@pytest.mark.django_db
def test_groups_endpoint(group_with_members):
    """Test /groups endpoint returns groups array"""
    response = APIClient().get('/groups/')
    assert response.status_code == 200
    assert response.json()[0]['displayName'] == group_with_members.display_name

