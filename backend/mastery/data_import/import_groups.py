import os
import json
from django.utils import timezone
import requests
from mastery import models

UDIR_GREP_URL = os.environ.get('UDIR_GREP_URL')

# Get data directory path
script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, "data")


def import_groups_from_file(org_number):
    """Import groups for ONE school from data_import/data/schools/<org>/groups.json"""
    print("👉 import_groups_from_file: BEGIN")

    groups_file = os.path.join(data_dir, org_number, "groups.json")
    if not os.path.exists(groups_file):
        raise Exception(
            f"Groups file not found for school {org_number}. Fetch groups first."
        )

    with open(groups_file, "r") as file:
        groups_data = json.load(file)

    basis_groups = groups_data.get("basis", [])
    teaching_groups = groups_data.get("teaching", [])
    groups_successfully_handled = 0
    errors = []
    yield {
        "result": {
            "entity": "group",
            "action": "import",
            "total_count": len(basis_groups) + len(teaching_groups),
            "success_count": 0,
            "failure_count": 0,
            "errors": [],
        },
        "is_done": False,
    }

    # Handle basis groups
    for index, group_data in enumerate(basis_groups, start=1):
        group, created, error = ensure_group_exists(group_data, "basis", None)
        if error:
            errors.append({"error": "ensure-basis-group-failed", "message": error})
        else:
            groups_successfully_handled += 1
        if index % 10 == 0:
            yield {
                "result": {
                    "entity": "group",
                    "action": "import",
                    "total_count": len(basis_groups) + len(teaching_groups),
                    "success_count": groups_successfully_handled,
                    "failure_count": len(errors),
                    "errors": errors,
                },
                "is_done": False,
            }

    # Handle teaching groups
    for index, group_data in enumerate(teaching_groups, start=1):
        subject = None
        if "grep" in group_data and "code" in group_data["grep"]:
            grep_code = group_data["grep"]["code"]
            subject, subject_was_created = ensure_subject_exists(grep_code)

        group, created, error = ensure_group_exists(group_data, "teaching", subject)
        if error:
            errors.append({"error": "ensure-teaching-group-failed", "message": error})
        else:
            groups_successfully_handled += 1
        if index % 10 == 0:
            yield {
                "result": {
                    "entity": "group",
                    "action": "import",
                    "total_count": len(basis_groups) + len(teaching_groups),
                    "success_count": groups_successfully_handled,
                    "failure_count": len(errors),
                    "errors": errors,
                },
                "is_done": False,
            }

    yield {
        "result": {
            "entity": "group",
            "action": "import",
            "total_count": len(basis_groups) + len(teaching_groups),
            "success_count": groups_successfully_handled,
            "failure_count": len(errors),
            "errors": errors,
        },
        "is_done": True,
    }


def ensure_group_exists(group_data, group_type, subject=None):
    """
    Create-or-update any group type.
    Returns (group, created_bool, error_message)
    """
    feide_id = group_data["id"]

    # Check if group already exists
    existing_group = models.Group.objects.filter(feide_id__exact=feide_id).first()
    if existing_group:
        print("Updated group:", feide_id)
        existing_group.display_name = group_data["displayName"]
        existing_group.subject = subject
        existing_group.valid_from = group_data.get("notBefore")
        existing_group.valid_to = group_data.get("notAfter")
        existing_group.maintained_at = timezone.now()
        existing_group.save()
        print("Updated group:", feide_id)
        return existing_group, False, None

    # Find parent school
    school = models.School.objects.filter(feide_id__exact=group_data["parent"]).first()
    if not school:
        return None, False, f"School not found for group {feide_id}"

    try:
        new_group = models.Group.objects.create(
            display_name=group_data["displayName"],
            type=group_type,
            school=school,
            subject=subject,
            feide_id=feide_id,
            valid_from=group_data.get("notBefore"),
            valid_to=group_data.get("notAfter"),
            maintained_at=timezone.now(),
        )
        print("Created group:", feide_id)
        return new_group, True, None

    except Exception as error:
        return None, False, f"Failed to create group {feide_id}: {str(error)}"


def ensure_subject_exists(grep_code):
    """Ensure a subject exists in the database, fetching from UDIR if necessary.
    Returns the subject instance and a boolean indicating if it was created.
    """
    # Check if subject already exists
    existing_subject = models.Subject.objects.filter(grep_code__exact=grep_code).first()
    if existing_subject:
        return existing_subject, False

    try:
        udir_response = requests.get(f"{UDIR_GREP_URL}/{grep_code}")
        if udir_response.status_code == 200 and udir_response.text:
            udir_subject = udir_response.json()
            display_name = udir_subject['tittel'][0]['verdi']
            short_name = udir_subject['kortform'][0]['verdi']
            grep_group_code = udir_subject['opplaeringsfag'][0]['kode'] if udir_subject.get(
                'opplaeringsfag') and len(udir_subject['opplaeringsfag']) > 0 else None

            subject = models.Subject.objects.create(
                display_name=display_name,
                short_name=short_name,
                grep_code=grep_code,
                grep_group_code=grep_group_code,
                maintained_at=timezone.now(),
            )
            print("Created subject:", grep_code, display_name)
            return subject, True
    except Exception as e:
        print("🚷Failed to fetch subject from UDIR:", {str(e)})
        return None, False
