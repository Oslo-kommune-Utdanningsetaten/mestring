import pytest
from rest_framework.test import APIClient


@pytest.fixture
def set_up_database(db):
    print("Setting up database")


@pytest.mark.django_db
def test_ping():
    """Test ping endpoint"""
    client = APIClient()
    resp = client.get('/api/ping/')
    assert resp.status_code == 200
    data = resp.json()
    assert data['api'] == 'up'
    assert data['db'] == 'up'
