import os
import json
import logging
import requests
import urllib.parse
from datetime import datetime
from django.shortcuts import redirect
from django.views.decorators.http import require_GET
from rest_framework.decorators import api_view
from rest_framework.response import Response
from oauthlib.oauth2 import WebApplicationClient
from mastery.models import User, School

FEIDE_CLIENT_ID = os.environ.get("FEIDE_CLIENT_ID")
FEIDE_CLIENT_SECRET = os.environ.get("FEIDE_CLIENT_SECRET")
FEIDE_DISCOVERY_URL = os.environ.get("FEIDE_DISCOVERY_URL")
FEIDE_USER_INFO_URL = os.environ.get("FEIDE_USER_INFO_URL")
FEIDE_CALLBACK = os.environ.get("FEIDE_CALLBACK")
FEIDE_LOGOUT_REDIR = os.environ.get("FEIDE_LOGOUT_REDIR")
FEIDE_REALM = os.environ.get("FEIDE_REALM")
FRONTEND = "http://localhost:5173"

logger = logging.getLogger(__name__)
client = WebApplicationClient(FEIDE_CLIENT_ID)
cached_provider_config = None


def get_provider_config():
    global cached_provider_config
    if not cached_provider_config:
        cached_provider_config = requests.get(FEIDE_DISCOVERY_URL).json()
    return cached_provider_config


def get_user_info():
    uri, headers, _ = client.add_token(FEIDE_USER_INFO_URL)
    return requests.get(uri, headers=headers).json()


def request_tokens_from_feide(code):
    provider_config = get_provider_config()
    token_endpoint = provider_config["token_endpoint"]
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        redirect_url=FEIDE_CALLBACK,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(FEIDE_CLIENT_ID, FEIDE_CLIENT_SECRET),
    )
    return client.parse_request_body_response(json.dumps(token_response.json()))


def check_affiliations(feide_user_id, affiliations):
    """
    Check if user has affiliation with an existing school.
    Returns a tuple (is_student_or_teacher, staff_at_schools)
    """
    if not feide_user_id or not affiliations:
        return [], [], []

    student_schools = []
    teacher_schools = []
    staff_schools = []
    for school in School.objects.all():
        org_number = school.org_number
        if f"student@{org_number}.feide.osloskolen.no" in affiliations:
            student_schools.append(school)
        if f"faculty@{org_number}.feide.osloskolen.no" in affiliations:
            teacher_schools.append(school)
        if f"staff@{org_number}.feide.osloskolen.no" in affiliations:
            staff_schools.append(school)
    return student_schools, teacher_schools, staff_schools


@require_GET
def feidelogin(request):
    provider_config = get_provider_config()
    authorization_endpoint = provider_config["authorization_endpoint"]
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=FEIDE_CALLBACK,
        scope=["openid", "userid", "profile", "userid-feide", "groups-org", "groups-edu"],
        login_hint=f"feide|realm|{FEIDE_REALM}",
    )
    return redirect(request_uri)


@require_GET
def feidecallback(request):
    code = request.GET.get("code", None)
    if not code:
        return redirect(FRONTEND)
    tokens = request_tokens_from_feide(code)
    user_info = get_user_info()
    feide_user_id = user_info.get("eduPersonPrincipalName", "").strip().lower()
    affiliations = user_info.get("eduPersonScopedAffiliation", [])

    # check if user has affiliation with an existing school
    student_schools, teacher_schools, staff_schools = check_affiliations(feide_user_id, affiliations)

    logger.debug(f"💁‍♀️ User {feide_user_id}")
    logger.debug(f"💁‍♀️ Student affiliations: {student_schools}")
    logger.debug(f"💁‍♀️ Teacher affiliations: {teacher_schools}")
    logger.debug(f"💁‍♀️ Staff affiliations: {staff_schools}")

    if student_schools or teacher_schools or staff_schools:
        # Student, teacher or staff at a known school --> allow login
        user, _ = User.objects.update_or_create(
            feide_id=feide_user_id,
            defaults={
                'name': user_info.get("displayName"),
                'email': feide_user_id.replace('@feide.', '@'),
                'last_activity_at': datetime.now()
            }
        )
        # Student and teacher roles are granted via imported groups
        # But ensure user gets staff role at all schools they are affiliated with
        if staff_schools:
            for school in staff_schools:
                school.add_staff(user, 'staff')

        request.session["feide_tokens"] = tokens
        request.session["feide_user_id"] = feide_user_id
        request.session["user_id"] = user.id
        return redirect(FRONTEND)
    request.session.clear()
    return redirect(f'{FRONTEND}?error=login_failed')


@require_GET
def feidelogout(request):
    tokens = request.session.get("feide_tokens")
    request.session.flush()
    if tokens and tokens.get("id_token"):
        provider_config = get_provider_config()
        end_session_endpoint = provider_config.get("end_session_endpoint")
        if end_session_endpoint:
            logout_params = {
                "post_logout_redirect_uri": FRONTEND,
                "id_token_hint": tokens["id_token"],
            }
            feide_logout_url = end_session_endpoint + "?" + urllib.parse.urlencode(logout_params)
            return redirect(feide_logout_url)
    return redirect(FRONTEND)


@api_view(['GET'])
def auth_status(request):
    user_id = request.session.get("user_id", None)
    if not user_id:
        return Response({"is_authenticated": False, "user": None})
    try:
        user = User.objects.get(id=user_id)
        return Response({
            "is_authenticated": True,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "feide_id": user.feide_id,
                "is_superadmin": getattr(user, 'is_superadmin', False),
            }
        })
    except User.DoesNotExist:
        request.session.flush()
        return Response({"is_authenticated": False, "user": None})
