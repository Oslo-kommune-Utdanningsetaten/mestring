import os
import json
import logging
import requests
import urllib.parse
from datetime import datetime
from django.shortcuts import redirect
from django.views.decorators.http import require_GET
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from oauthlib.oauth2 import WebApplicationClient
from mastery.models import User, School

FEIDE_CLIENT_ID = os.environ.get("FEIDE_CLIENT_ID")
FEIDE_CLIENT_SECRET = os.environ.get("FEIDE_CLIENT_SECRET")
FEIDE_DISCOVERY_URL = os.environ.get("FEIDE_DISCOVERY_URL")
FEIDE_USER_INFO_URL = os.environ.get("FEIDE_USER_INFO_URL")
FEIDE_CALLBACK = os.environ.get("FEIDE_CALLBACK")
FEIDE_LOGOUT_REDIR = os.environ.get("FEIDE_LOGOUT_REDIR")
FEIDE_REALM = os.environ.get("FEIDE_REALM")
FRONTEND = os.environ.get("FRONTEND")

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


def check_affiliations(feide_user_id, feide_affiliations):
    """
    Check if user has affiliation with an existing school which has been enabled.
    Returns a dict with affiliated schools and messages
    """
    result = {
        "student_schools": [],
        "teacher_schools": [],
        "staff_schools": [],
        "messages": []
    }
    if not feide_user_id or not feide_affiliations:
        return result

    for school in School.objects.all():
        org_number = school.org_number
        if f"student@{org_number}.feide.osloskolen.no" in feide_affiliations:
            if school.is_service_enabled:
                result["student_schools"].append(school)
            else:
                result["messages"].append(
                    f"Du er elev ved {school.display_name}, men skolen har ikke aktivert tjenesten.")
        if f"faculty@{org_number}.feide.osloskolen.no" in feide_affiliations:
            if school.is_service_enabled:
                result["teacher_schools"].append(school)
            else:
                result["messages"].append(
                    f"Du er lærer ved {school.display_name}, men skolen har ikke aktivert tjenesten.")
        if f"staff@{org_number}.feide.osloskolen.no" in feide_affiliations:
            if school.is_service_enabled:
                result["staff_schools"].append(school)
            else:
                result["messages"].append(
                    f"Du er ansatt ved {school.display_name}, men skolen har ikke aktivert tjenesten.")

    return result


@require_GET
@permission_classes([AllowAny])
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
@permission_classes([AllowAny])
def feidecallback(request):
    code = request.GET.get("code", None)
    if not code:
        return redirect(FRONTEND)
    tokens = request_tokens_from_feide(code)
    user_info = get_user_info()
    feide_user_id = user_info.get("eduPersonPrincipalName", "").strip().lower()
    feide_affiliations = user_info.get("eduPersonScopedAffiliation", [])

    # check if user has affiliation with an enabled school in the system
    system_affiliations = check_affiliations(feide_user_id, feide_affiliations)
    student_schools = system_affiliations["student_schools"]
    teacher_schools = system_affiliations["teacher_schools"]
    staff_schools = system_affiliations["staff_schools"]
    messages = system_affiliations["messages"]

    logger.debug(f"💁‍♀️ User {feide_user_id}")
    logger.debug(f"💁‍♀️ Student affiliations: {student_schools}")
    logger.debug(f"💁‍♀️ Teacher affiliations: {teacher_schools}")
    logger.debug(f"💁‍♀️ Staff affiliations: {staff_schools}")
    logger.debug(f"💁‍♀️ Messages: {messages}")

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
        # But ensure user gets staff role at schools they are affiliated with
        if staff_schools:
            for school in staff_schools:
                school.set_employed_user(user, 'staff')

        request.session["feide_tokens"] = tokens
        request.session["feide_user_id"] = feide_user_id
        request.session["user_id"] = user.id
        return redirect(FRONTEND)
    else:
        # Is there a superadmin with this feide_id?
        superadmin_user = User.objects.filter(feide_id=feide_user_id, is_superadmin=True).first()
        if superadmin_user:
            request.session["feide_tokens"] = tokens
            request.session["feide_user_id"] = feide_user_id
            request.session["user_id"] = superadmin_user.id
            return redirect(FRONTEND)
        else:
            # No affiliated schools found --> deny login
            request.session.clear()
            error_message = ' '.join(messages) or "login_failed"
            return redirect(f'{FRONTEND}?error={error_message}')


@require_GET
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
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
