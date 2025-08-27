import os
import json
import requests
import urllib.parse
from datetime import datetime
from django.shortcuts import redirect
from django.views.decorators.http import require_GET
from rest_framework.decorators import api_view
from rest_framework.response import Response
from oauthlib.oauth2 import WebApplicationClient
from mastery.models import User

FEIDE_CLIENT_ID = os.environ.get("FEIDE_CLIENT_ID")
FEIDE_CLIENT_SECRET = os.environ.get("FEIDE_CLIENT_SECRET")
FEIDE_DISCOVERY_URL = os.environ.get("FEIDE_DISCOVERY_URL")
FEIDE_CALLBACK = os.environ.get("FEIDE_CALLBACK")
FEIDE_LOGOUT_REDIR = os.environ.get("FEIDE_LOGOUT_REDIR")
FEIDE_REALM = "feide.osloskolen.no"
FRONTEND = "http://localhost:5173"

client = WebApplicationClient(FEIDE_CLIENT_ID)


def get_provider_config():
    return requests.get(FEIDE_DISCOVERY_URL).json()


def get_user_info(userinfo_endpoint):
    uri, headers, body = client.add_token(userinfo_endpoint)
    return requests.get(uri, headers=headers, data=body).json()


@require_GET
def feidelogin(request):
    feide_provider_config = get_provider_config()
    authorization_endpoint = feide_provider_config["authorization_endpoint"]
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=FEIDE_CALLBACK,
        scope=["openid", "userid", "profile", "userid-feide", "groups-org", "groups-edu"],
        login_hint=f"feide|realm|{FEIDE_REALM}",
    )
    return redirect(request_uri)


@require_GET
def feidecallback(request):
    code = request.GET.get("code", "")
    if not code:
        return redirect(FRONTEND)
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
    tokens = client.parse_request_body_response(json.dumps(token_response.json()))
    user_info = get_user_info(provider_config["userinfo_endpoint"])
    principal_name = user_info.get("https://n.feide.no/claims/eduPersonPrincipalName")
    if principal_name:
        feide_user_id = principal_name.strip().lower()
        request.session["feide_tokens"] = tokens
        request.session["feide_user_id"] = feide_user_id
        try:
            user = User.objects.get(feide_id=feide_user_id)
            user.name = user_info.get("name", user.name)
            user.email = feide_user_id.replace('@feide.', '@')
            user.last_activity_at = datetime.now()
            user.save()
            request.session["user_id"] = user.id
        except User.DoesNotExist:
            # TODO: Only create user if affiliated with a known school
            user = User.objects.create(
                feide_id=feide_user_id,
                name=user_info.get("name", user.name),
                email=feide_user_id.replace('@feide.', '@'),
                last_activity_at=datetime.now()
            )
            request.session["user_id"] = user.id
        return redirect(FRONTEND)
    request.session.clear()
    return redirect(f'{FRONTEND}?error=login_failed')


@require_GET
def feidelogout(request):
    tokens = request.session.get("feide_tokens")
    request.session.flush()
    if tokens and tokens.get("id_token"):
        cfg = get_provider_config()
        end_session_endpoint = cfg.get("end_session_endpoint")
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
