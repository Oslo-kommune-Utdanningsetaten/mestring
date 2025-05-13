import os
import sys
import json
import requests
from dotenv import load_dotenv

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)
load_dotenv(os.path.join(project_root, '.env'))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()
from mastery import models

TOKEN_ENDPOINT = "https://auth.dataporten.no/oauth/token"
GROUPS_ENDPOINT = "https://groups-api.dataporten.no/groups/orgs/feide.osloskolen.no/groups/"
FEIDE_PUBLIC_KEY = os.environ.get('FEIDE_PUBLIC_KEY')
FEIDE_PRIVATE_KEY = os.environ.get('FEIDE_PRIVATE_KEY')

def create_user_item(member):
    feide_id = member['userid_sec'][0]
    email = feide_id.split(':')[1].replace('@feide.', '@')
    return {
        "feide_id": feide_id,
        "name": member['name'],
        "email": email,
        "affiliation": member['membership'].get('affiliation', None)
    }

def fetch_and_store_feide_users():
    print("BEGIN: fetch_and_store_feide_users")
    # Check if credentials are set
    if not FEIDE_PUBLIC_KEY or not FEIDE_PRIVATE_KEY:
        print("Error: FEIDE_PUBLIC_KEY or FEIDE_PRIVATE_KEY environment variables not set")
        return

    # Get token
    token_response = requests.post(TOKEN_ENDPOINT, auth=(FEIDE_PUBLIC_KEY, FEIDE_PRIVATE_KEY), data={'grant_type': 'client_credentials'})

    if token_response.status_code == 200 and token_response.text:
        token = token_response.json()['access_token']
    else:
        print(f"🚷Failed to get token. Status code: {token_response.status_code}")
        return

    known_groups = models.Group.objects.all()
    result = {}

    for known_group in known_groups:
        print(f"Fetching members of group: {known_group.feide_id}")
        members_response = requests.get(GROUPS_ENDPOINT + known_group.feide_id.replace('%', '%25') + "/members", headers={"Authorization": "Bearer " + token})
        if members_response.status_code != 200:
            print(f"Failed 🚷{members_response.status_code} to fetch members of : {known_group.feide_id}")
            continue
        if known_group.feide_id not in result:
            result[known_group.feide_id] = {
                "teachers": [],
                "students": [],
                "other": []
            }
        feide_group_members = members_response.json()
        for feide_member in feide_group_members:
            member_item = create_user_item(feide_member)
            if member_item['affiliation'] == 'student':
                result[known_group.feide_id]['students'].append(member_item)
            elif member_item['affiliation'] == 'faculty':
                result[known_group.feide_id]['teachers'].append(member_item)
            else:
                result[known_group.feide_id]['other'].append(member_item)

    output_file = os.path.join(script_dir, 'data', 'users.json')
    with open(output_file, "w") as file:
        json.dump(result, file, indent=2, ensure_ascii=False)
    print("END: fetch_and_store_feide_users")


if __name__ == "__main__":
    fetch_and_store_feide_users()
