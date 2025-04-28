import pytest
from django.test import RequestFactory
from rest_framework.test import force_authenticate
from mastery.models import School
from mastery.views import SchoolViewSet


@pytest.fixture
def set_up_database(db):
    return School.objects.create(
        feide_id="fc:org:kakrafoon.kommune.no:unit:NO987654321",
        display_name="Kakrafoon vgs",
        org_number="U87654321",
        owner="kakrafoon.kommune.no",
    )


@pytest.mark.django_db
def test_schools_endpoint(set_up_database):
    """Test /schools endpoint returns school array"""
    from rest_framework.test import APIClient
    
    client = APIClient()
    response = client.get('/schools/')  # Use your actual URL pattern
    
    # Check response is JSON and parse it
    assert response.status_code == 200
    
    # Now we're checking the actual rendered JSON with camelCase
    assert response.json()[0]['displayName'] == 'Kakrafoon vgs'
