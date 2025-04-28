import pytest
from django.test import RequestFactory
from mastery.models import School
from mastery.views import SchoolViewSet
from unittest.mock import patch


@pytest.fixture
def set_up_database(db, request):
    School.objects.create(
        feide_id = "fc:org:kakrafoon.kommune.no:unit:NO987654321",	
        display_name = "Kakrafoon vgs",
        org_number = "U87654321",
        owner = "kakrafoon.kommune.no",
    )


@pytest.mark.django_db(reset_sequences=True)
def test_schools_endpoint(set_up_database):
    """/schools endpoint returns shools array"""
    excepted = [{'displayName': 'Eksempelskole'}]
    request = RequestFactory().get('/schools')
    response = SchoolViewSet(request)
    assert response.status_code == 200
    assert response.data == excepted

