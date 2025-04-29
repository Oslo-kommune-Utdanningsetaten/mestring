import pytest
from django.test import Client
from mastery.models import School

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

@pytest.fixture
def school(db):
    return School.objects.create(
        feide_id="fc:org:kakrafoon.kommune.no:unit:NO987654321",
        display_name="Kakrafoon vgs",
        org_number="987654321",
        owner="kakrafoon.kommune.no",
    )