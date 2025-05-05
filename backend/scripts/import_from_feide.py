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
        
def get_groups(url, token, result):
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

    # Check for pagination
    if 'Link' in groups_response.headers:
        next_url = None
        link_header = CaseInsensitiveDict(groups_response.headers)['Link']
        links = requests.utils.parse_header_links(link_header)

        for link in links:
            if 'rel' in link and link['rel'] == 'next':
                next_url = link['url']
                break

    return result, next_url


def fetch_groups_helper():
    print("fetch_groups called")

    # Check if credentials are set
    if not FEIDE_PUBLIC_KEY or not FEIDE_PRIVATE_KEY:
        print("Error: FEIDE_PUBLIC_KEY or FEIDE_PRIVATE_KEY environment variables not set")
        return

    # Add debug print to see what's being sent
    print(f"Requesting token from {TOKEN_ENDPOINT}")

    token_response = requests.post(TOKEN_ENDPOINT, auth=(FEIDE_PUBLIC_KEY, FEIDE_PRIVATE_KEY), data={'grant_type': 'client_credentials'})

    print(f"Response status code: {token_response.status_code}")
    
    if token_response.status_code == 200 and token_response.text:
        token = token_response.json()['access_token']
    else:
        print(f"Failed to get token. Status code: {token_response.status_code}")
        return

    result = {}
    next_url = GROUPS_ENDPOINT

    i = 0
    while next_url and i < 10:
        i += 1
        print("Fetching groups:", i)
        print("  --> ", next_url)
        result, next_url = get_groups(next_url, token, result)
    print("  ZAAAAA ", result)

    output_file = os.path.join(project_root, 'groups.json')
    print(f"Writing results to: {output_file}")
    with open(output_file, "w") as file:
        json.dump(result, file, indent=2)

    print("len of groups_result", len(result))



# Loop through schools, add missing info from udir national schoolregister
def handle_schools_helper():
    with open("./groups.json") as file:
        groups = json.load(file)

    count = 0
    schools = (groups['fc:org'].get("['primary_and_lower_secondary', 'upper_secondary']", []) +
               groups['fc:org'].get("['upper_secondary', 'primary_and_lower_secondary']", []))

    for school in schools:
        school_org_number = school["id"].rsplit(':', 1)[-1]
        try:
            django.db.close_old_connections()   
            existing_school = models.School.objects.get(org_number__exact=school_org_number)
        except ObjectDoesNotExist:
            existing_school = False
            count += 1

            try:
                school_search_response = requests.get("https://nsr.udir.no/api/enheter/underenhetStandard/" + school["id"].rsplit(':NO', 1)[-1])
                school_search_json = school_search_response.json()
                school_search_name = school_search_json['navn']
            except:
                school_search_name = None
                print("error fetching school name from udir for school:", school['displayName'])

        if existing_school:
            if len(school['displayName']) == 3:
                existing_school.short_name = school['displayName']
            existing_school.save()
        
        elif school_search_name is not None:
            new_school = models.School.objects.create(name=school_search_name, org_number=school_org_number)
            if len(school['displayName']) == 3:
                new_school.short_name = school['displayName']
                new_school.save()
        else:
            new_school_no_name = models.School.objects.create(name=school['displayName'], org_number=school_org_number)
            if len(school['displayName']) == 3:
                new_school_no_name.short_name = school['displayName']
                new_school_no_name.save()

    print("schools added:", count)


if __name__ == "__main__":
    # Parse command line arguments or control which functions run
    fetch_groups_helper()
    # handle_schools_helper()
