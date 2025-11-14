import json
import pytest
from rest_framework.test import APIClient

PING_URL = '/api/ping/'
SUBJECTS_URL = '/api/subjects/'

# Use custom login logic, because force_authenticate bypasses authenticate in SessionUserIdAuthentication


def login_client_as(client: APIClient, user) -> None:
    session = client.session
    session['user_id'] = user.id
    session.save()


@pytest.mark.django_db
def test_get_ping_does_not_require_csrf():
    client = APIClient(enforce_csrf_checks=True)
    response = client.get(PING_URL)
    assert response.status_code == 200
    assert 'csrftoken' in response.cookies


@pytest.mark.django_db
def test_post_subject_with_valid_csrf_token_succeeds(superadmin, school):
    client = APIClient(enforce_csrf_checks=True)
    login_client_as(client, superadmin)
    response = client.get(PING_URL)
    csrftoken = response.cookies['csrftoken'].value

    payload = {
        'displayName': 'CSRF ok',
        'shortName': 'ok',
        'ownedBySchoolId': school.id,
    }
    response = client.post(
        SUBJECTS_URL,
        data=json.dumps(payload),
        content_type='application/json',
        HTTP_X_CSRFTOKEN=csrftoken,
    )
    assert response.status_code == 201


@pytest.mark.django_db
def test_post_subject_without_csrf_token_is_rejected(superadmin, school):
    client = APIClient(enforce_csrf_checks=True)
    login_client_as(client, superadmin)
    client.get(PING_URL)

    payload = {
        'displayName': 'CSRF missing',
        'shortName': 'missing',
        'ownedBySchoolId': school.id,
    }
    response = client.post(
        SUBJECTS_URL,
        data=json.dumps(payload),
        content_type='application/json',
    )
    assert response.status_code == 403
