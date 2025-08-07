import os
import json
import requests
import urllib.parse
from datetime import datetime
from django.shortcuts import redirect
from django.views.decorators.http import require_GET
from django.conf import settings
from django.http import JsonResponse
from oauthlib.oauth2 import WebApplicationClient
from .models import User

FEIDE_CLIENT_ID = os.environ.get("FEIDE_CLIENT_ID")
FEIDE_CLIENT_SECRET = os.environ.get("FEIDE_CLIENT_SECRET")
FEIDE_DISCOVERY_URL = os.environ.get("FEIDE_DISCOVERY_URL")
FEIDE_CALLBACK = os.environ.get("FEIDE_CALLBACK")
FEIDE_LOGOUT_REDIR = os.environ.get("FEIDE_LOGOUT_REDIR")
FEIDE_REALM = "feide.osloskolen.no"
FRONTEND = "http://localhost:5173" 

client = WebApplicationClient(FEIDE_CLIENT_ID)

def get_provider_cfg():
    return requests.get(FEIDE_DISCOVERY_URL).json()


@require_GET
def feidelogin(request):
    feide_provider_cfg = get_provider_cfg()
    authorization_endpoint = feide_provider_cfg["authorization_endpoint"]

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=FEIDE_CALLBACK,
        scope=["openid", "userid", "profile", "userid-feide", "groups-org", "groups-edu"],
        login_hint=f"feide|realm|{FEIDE_REALM}",
    )
    return redirect(request_uri)


@require_GET
def feidecallback(request):
    """Handle OAuth callback from Feide"""
    code = request.GET.get("code", "")
    
    if not code:
        return redirect(FRONTEND)

    provider_cfg = get_provider_cfg()
    token_endpoint = provider_cfg["token_endpoint"]

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
    
    userinfo_endpoint = provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    principal_name = userinfo_response.json().get("https://n.feide.no/claims/eduPersonPrincipalName")

    if principal_name:
        feide_user_id = principal_name.strip().lower()
        # Store tokens in session
        request.session["feide_tokens"] = tokens
        request.session["feide_user_id"] = feide_user_id
               
        # Check if user exists in database
        try:
            user = User.objects.get(feide_id=feide_user_id)
            print(f"Found existing user: {user.id}")
            
            # Update existing user info
            user.name = userinfo_response.json().get("name", user.name)
            user.email = feide_user_id.replace('@feide.', '@')
            user.last_activity_at = datetime.now()
            user.save()
            
            # Store user_id in session
            request.session["user_id"] = user.id
            
        except User.DoesNotExist:
            print(f"User not found in database: {feide_user_id}")
                    
        return redirect(FRONTEND)
    else:
        request.session.clear()
        return redirect(f'{FRONTEND}?error=login_failed')
    

@require_GET
def feidelogout(request):
    """Logout from Feide and clear session"""
    tokens = request.session.get("feide_tokens")
    request.session.flush()
    
    if tokens and tokens.get("id_token"):
        cfg = get_provider_cfg()
        end_session_endpoint = cfg.get("end_session_endpoint")
        
        if end_session_endpoint:
            logout_params = {
                "post_logout_redirect_uri": FRONTEND,
                "id_token_hint": tokens["id_token"],
            }
            feide_logout_url = end_session_endpoint + "?" + urllib.parse.urlencode(logout_params)
            return redirect(feide_logout_url)
    
    return redirect(FRONTEND)


@require_GET
def auth_status(request):
    """Check if there is a sessoion user, and it matches it matches a db entry"""
    user_id = request.session.get('user_id', None)
    # Check if user exists in database
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            return JsonResponse({
                "authenticated": True,
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "feide_id": user.feide_id,
                    "is_superadmin": user.is_superadmin,
                }
            })
        except User.DoesNotExist:
            pass
        
    return JsonResponse({"authenticated": False})
