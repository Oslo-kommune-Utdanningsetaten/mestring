import pytest
from django.test import Client

# Basic fixture for Django client
@pytest.fixture
def client():
    return Client()

# Fixture for authenticated client
@pytest.fixture
def auth_client(db, client):
    # Implement authentication logic here
    # For example:
    # from django.contrib.auth import get_user_model
    # User = get_user_model()
    # user = User.objects.create_user(username='testuser', password='password')
    # client.force_login(user)
    return client

# Fixture to provide a test School object
@pytest.fixture
def school(db):
    from mastery.models import School
    return School.objects.create(
        feide_id="fc:org:test.school.no:unit:NO123456789",
        display_name="Test School",
        org_number="U12345678",
        owner="test.kommune.no"
    )