import os
import sys
import json
import requests
from requests.structures import CaseInsensitiveDict
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)
load_dotenv(os.path.join(project_root, '.env'))


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


def _fetch_groups(url, token, result):
    groups_response = requests.get(url, headers={"Authorization": "Bearer " + token})
    groups = groups_response.json()

    # Append groups to accumulated result
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

    # Check for pagination
    next_url = None
    if 'Link' in groups_response.headers:
        link_header = CaseInsensitiveDict(groups_response.headers)['Link']
        links = requests.utils.parse_header_links(link_header)
        for link in links:
            if 'rel' in link and link['rel'] == 'next':
                next_url = link['url']
                break

    return result, next_url


def fetch_and_store_feide_groups():
    print("👉 fetch_and_store_feide_groups: BEGIN")
    # Check if credentials are set
    if not FEIDE_PUBLIC_KEY or not FEIDE_PRIVATE_KEY:
        print("Error: FEIDE_PUBLIC_KEY or FEIDE_PRIVATE_KEY environment variables not set")
        return

    # Get token
    token_response = requests.post(TOKEN_ENDPOINT, auth=(FEIDE_PUBLIC_KEY, FEIDE_PRIVATE_KEY), data={'grant_type': 'client_credentials'})

    if token_response.status_code == 200 and token_response.text:
        token = token_response.json()['access_token']
    else:
        print(f"Failed to get token. Status code: {token_response.status_code}")
        return

    result = {}
    next_url = GROUPS_ENDPOINT

    while next_url:
        result, next_url = _fetch_groups(next_url, token, result)

    output_file = os.path.join(script_dir, 'data', 'groups.json')
    with open(output_file, "w") as file:
        json.dump(result, file, indent=2, ensure_ascii=False)

    print("✅ fetch_and_store_feide_groups: DONE")


if __name__ == "__main__":
    fetch_and_store_feide_groups()
