import os
import sys
import django

# Set up Django environment using relative paths
# Get the absolute path of the directory containing this script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory (the Django project root)
project_root = os.path.abspath(os.path.join(script_dir, '..'))
# Add the project root to Python path
sys.path.append(project_root)
# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

from dotenv import load_dotenv
# Load from .env in project root
load_dotenv(os.path.join(project_root, '.env'))
django.setup()

import json
import requests
from django.db.models.base import ObjectDoesNotExist
from mastery import models, serializers
from requests.structures import CaseInsensitiveDict
import django.db
from requests.auth import HTTPBasicAuth

TOKEN_ENDPOINT = "https://auth.dataporten.no/oauth/token"
GROUPS_ENDPOINT = "https://groups-api.dataporten.no/groups/orgs/feide.osloskolen.no/groups"
FEIDE_PUBLIC_KEY = os.environ.get('FEIDE_PUBLIC_KEY')
FEIDE_PRIVATE_KEY = os.environ.get('FEIDE_PRIVATE_KEY')


def _get_type_type_key(type):
    match type:
        case 'fc:gogroup':
            return 'go_type'
        case 'fc:grep2':
            return 'grep_type'
        case 'fc:org':
            return 'orgType'
        
def _get_groups(url, token, result):
    # Fetch groups from the API
    groups_response = requests.get(url, headers={"Authorization": "Bearer " + token})
    groups = groups_response.json()

    # Append groups to result
    for group in groups:
        type = group['type']
        type_type_key = _get_type_type_key(type)

        g = result.get(type, None)
        if g is None:
            result[type] = {}

        gg = result[type].get(str(group[type_type_key]), None)
        if gg is None:
            result[type][str(group[type_type_key])] = []

        result[type][str(group[type_type_key])].append(group)

    next_url = None
    # Check for pagination
    if 'Link' in groups_response.headers:
        link_header = CaseInsensitiveDict(groups_response.headers)['Link']
        links = requests.utils.parse_header_links(link_header)
        for link in links:
            if 'rel' in link and link['rel'] == 'next':
                next_url = link['url']
                break

    return result, next_url


def fetch_groups_helper():
    # Check if credentials are set
    if not FEIDE_PUBLIC_KEY or not FEIDE_PRIVATE_KEY:
        print("Error: FEIDE_PUBLIC_KEY or FEIDE_PRIVATE_KEY environment variables not set")
        return

    token_response = requests.post(TOKEN_ENDPOINT, auth=(FEIDE_PUBLIC_KEY, FEIDE_PRIVATE_KEY), data={'grant_type': 'client_credentials'})

    if token_response.status_code == 200 and token_response.text:
        token = token_response.json()['access_token']
    else:
        print(f"Failed to get token. Status code: {token_response.status_code}")
        return

    result = {}
    next_url = GROUPS_ENDPOINT

    i = 0
    while next_url:
        i += 1
        print("Fetch:", i, next_url, '\n')
        result, next_url = _get_groups(next_url, token, result)

    output_file = os.path.join(script_dir, 'data', 'groups.json')
    with open(output_file, "w") as file:
        json.dump(result, file, indent=2)

    print("Done!", i)


if __name__ == "__main__":
    # Parse command line arguments or control which functions run
    fetch_groups_helper()
    # handle_schools_helper()
