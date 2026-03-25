import json
import os
import requests
import logging
import names
import random

script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, "data")

FEIDE_CLIENT_ID = os.environ.get("FEIDE_CLIENT_ID")
FEIDE_CLIENT_SECRET = os.environ.get("FEIDE_CLIENT_SECRET")
TOKEN_URL = os.environ.get("TOKEN_URL")

logger = logging.getLogger(__name__)


def get_feide_access_token():
    try:
        response = requests.post(
            TOKEN_URL,
            data={"grant_type": "client_credentials"},
            auth=(FEIDE_CLIENT_ID, FEIDE_CLIENT_SECRET),
        )
        response.raise_for_status()
        return response.json()["access_token"]
    except Exception as e:
        raise Exception(f"Failed to get Feide access token: {e}")


fake_users_by_feide_id = {}


def create_user_item(member, anonymize=False):
    """Helper function to create user item from Feide member data"""
    feide_id = member["userid_sec"][0].split(":")[1]
    email = feide_id.replace("@feide.", "@")

    # Feide might provide affiliation as string or list
    feide_affiliations = member["membership"].get("affiliation", [])
    if isinstance(feide_affiliations, str):
        affiliations = [feide_affiliations]
    else:
        affiliations = feide_affiliations if isinstance(feide_affiliations, list) else []

    if anonymize:
        # If anonymization is requested, generate fake users, consistent accross groups
        if fake_users_by_feide_id.get(feide_id):
            # Reuse previously generated fake user for this feide_id
            user_item = fake_users_by_feide_id[feide_id]
        else:
            # Generate new fake user
            first_name = names.get_first_name()
            last_name = names.get_last_name()
            anon_feide_id = first_name[0:3] + last_name[0:3] + str(
                random.randrange(0, 1000)).zfill(3) + '@feide.osloskolen.no'
            user_item = {}
            user_item["name"] = f"{first_name} {last_name}"
            user_item["feide_id"] = anon_feide_id
            user_item["email"] = anon_feide_id.replace("@feide.", "@")
            user_item["affiliations"] = affiliations
            fake_users_by_feide_id[feide_id] = user_item
    else:
        # Return actual user data
        user_item = {
            "feide_id": feide_id,
            "name": member["name"],
            "email": email,
            "affiliations": affiliations,
        }
    return user_item


def does_file_exist(org_number, type):
    school_dir = os.path.join(data_dir, org_number)
    return os.path.exists(os.path.join(school_dir, f"{type}.json"))


def load_school_data(org_number, file_type):
    """Load and parse JSON data file for school"""
    file_path = os.path.join(data_dir, org_number, f"{file_type}.json")

    if not os.path.exists(file_path):
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Failed to read {file_type}.json for {org_number}: {e}")
        return None


def count_fetched_groups(org_number):
    """Count groups from fetched data"""
    groups_data = load_school_data(org_number, 'groups')
    if not groups_data:
        return None

    basis_count = len(groups_data.get('basis', []))
    teaching_count = len(groups_data.get('teaching', []))
    return basis_count + teaching_count


def count_fetched_memberships_and_users(org_number):
    """Count unique users and total memberships from fetched data"""
    memberships_data = load_school_data(org_number, 'memberships')
    if memberships_data is None:
        return None, None

    if not memberships_data:
        return 0, 0

    unique_users = set()
    total_memberships = 0

    for group_data in memberships_data.values():
        if not isinstance(group_data, dict):
            continue

        # Count all members (teachers + students + other)
        for member_list in [
                group_data.get('teachers', []),
                group_data.get('students', []),
                group_data.get('other', [])]:
            for member in member_list:
                if isinstance(member, dict) and 'feide_id' in member:
                    unique_users.add(member['feide_id'])
                    total_memberships += 1

    return len(unique_users), total_memberships


def get_school_fetched_stats(org_number):
    """Get all fetched statistics for a school"""
    groups_count = count_fetched_groups(org_number)
    users_count, memberships_count = count_fetched_memberships_and_users(org_number)

    return {
        "groups_count": groups_count,
        "users_count": users_count,
        "memberships_count": memberships_count
    }
