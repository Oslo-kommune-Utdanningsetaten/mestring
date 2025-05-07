import os
import sys
import json
import requests
from dotenv import load_dotenv

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)
load_dotenv(os.path.join(project_root, '.env'))


TOKEN_ENDPOINT = "https://auth.dataporten.no/oauth/token"
GROUPS_ENDPOINT = "https://groups-api.dataporten.no/groups/orgs/feide.osloskolen.no/groups"
FEIDE_PUBLIC_KEY = os.environ.get('FEIDE_PUBLIC_KEY')
FEIDE_PRIVATE_KEY = os.environ.get('FEIDE_PRIVATE_KEY')


def _fetch_groups(url, token, result):
    groups_response = requests.get(url, headers={"Authorization": "Bearer " + token})
    groups = groups_response.json()

    # Append groups to accumulated result
    for group in groups:
        group_type = group['type']
        group_go_type = group.get('go_type', None)
        group_grep_type = group.get('grep_type', None)

        # by definition, only schools have the parent key
        # https://docs.feide.no/reference/apis/groups_api/group_types/pse_school_owner.html
        if group_type == 'fc:org':
            if 'parent' in group:
                result['schools'].append(group)
            else:
                result['owners'].append(group)            
        elif group_type == 'fc:gogroup' and group_go_type == 'u':
            result['teaching'].append(group)
        elif group_type == 'fc:gogroup' and group_go_type == 'b':
            result['basis'].append(group)
        elif group_type == 'fc:grep2' and group_grep_type == 'fagkoder':
            result['subjects'].append(group)
        elif group_type == 'fc:grep2' and group_grep_type == 'utdanningsprogram':
            result['programs'].append(group)
        elif group_type == 'fc:grep2' and group_grep_type == 'aarstrinn':
            result['levels'].append(group)
        else:
            result['other'].append(group)

    # Check for pagination
    next_url = None
    if 'Link' in groups_response.headers:
        link_header = requests.structures.CaseInsensitiveDict(groups_response.headers)['Link']
        links = requests.utils.parse_header_links(link_header)
        for link in links:
            if 'rel' in link and link['rel'] == 'next':
                next_url = link['url']
                break

    return result, next_url


def fetch_and_store_feide_groups():
    print("BEGIN: fetch_and_store_feide_groups")
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

    result = {
        "owners": [],   # skoleeiere
        "schools": [],  # skoler
        "teaching": [], # undervisningsgrupper
        "basis": [],    # basisgrupper  
        "subjects": [], # fag
        "programs": [], # utdanningsprogrammer
        "levels": [],   # årstrinn
        "other": [],    # andre grupper vi kan ha interesse av?
    }
    next_url = GROUPS_ENDPOINT
    while next_url:
        # keep fetching until there are no more pages
        result, next_url = _fetch_groups(next_url, token, result)

    output_file = os.path.join(script_dir, 'data', 'groups.json')
    with open(output_file, "w") as file:
        json.dump(result, file, indent=2, ensure_ascii=False)
    print("END: fetch_and_store_feide_groups")


if __name__ == "__main__":
    fetch_and_store_feide_groups()
