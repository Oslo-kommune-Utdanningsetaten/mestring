import os
import requests

script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, "data")

FEIDE_CLIENT_ID = os.environ.get("FEIDE_CLIENT_ID")
FEIDE_CLIENT_SECRET = os.environ.get("FEIDE_CLIENT_SECRET")
TOKEN_URL = os.environ.get("TOKEN_URL")


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


def create_user_item(member):
    """Helper function to create user item from Feide member data"""
    feide_id = member["userid_sec"][0].split(":")[1]
    email = feide_id.replace("@feide.", "@")
    return {
        "feide_id": feide_id,
        "name": member["name"],
        "email": email,
        "affiliation": member["membership"].get("affiliation", None),
    }


# def check_school_data_status(org_number):
#     """Check what data files exist for a school"""
#     school_dir = os.path.join(data_dir, org_number)

#     status = {
#         "groups_file_exists": os.path.exists(os.path.join(school_dir, "groups.json")),
#         "users_file_exists": os.path.exists(os.path.join(school_dir, "users.json")),
#     }

#     return status
def does_file_exist(org_number, type):  
    school_dir = os.path.join(data_dir, org_number)  
    return os.path.exists(os.path.join(school_dir, f"{type}.json"))  
