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

    with open(groups_file, "r", encoding="utf-8") as file:
        groups_data = json.load(file)

    # Progress reporting variables
    groups_created = 0
    groups_maintained = 0
    groups_failed = 0
    subjects_created = 0
    subject_maintained = 0
    subjects_failed = 0
    errors = []

    basis_groups = groups_data.get("basis", [])
    teaching_groups = groups_data.get("teaching", [])

    # Handle basis groups
    for index, group_data in enumerate(basis_groups, start=1):
        _, created, group_error = ensure_group_exists(group_data, "basis", None)
        if group_error:
            errors.append({"error": "ensure-basis-group-failed", "message": group_error})
            groups_failed += 1
        elif created:
            groups_created += 1
        else:
            groups_maintained += 1

        if index % 10 == 0:
            yield {
                "result": {
                    "entity": "group",
                    "action": "import",
                    "errors": errors,
                    "changes": {
                        "group": {
                            "created": groups_created,
                            "maintained": groups_maintained,
                            "failed": groups_failed,
                        },
                        "subject": {
                            "created": subjects_created,
                            "maintained": subject_maintained,
                            "failed": subjects_failed,
                        },
                    },
                },
                "is_done": False,
            }

    # Handle teaching groups
    for index, group_data in enumerate(teaching_groups, start=1):
        subject = None
        if "grep" in group_data and "code" in group_data["grep"]:
            grep_code = group_data["grep"]["code"]
            if grep_code:
                subject, subject_was_created, subject_error = ensure_subject_exists(grep_code)

                if subject_error:
                    subjects_failed += 1
                    errors.append({"error": "ensure-subject-failed", "message": subject_error})
                elif subject_was_created:
                    subjects_created += 1
                else:
                    subject_maintained += 1

        _, created, group_error = ensure_group_exists(group_data, "teaching", subject)
        if group_error:
            errors.append({"error": "ensure-teaching-group-failed", "message": group_error})
            groups_failed += 1
        elif created:
            groups_created += 1
        else:
            groups_maintained += 1

        if index % 10 == 0:
            yield {
                "result": {
                    "entity": "group",
                    "action": "import",
                    "errors": errors,
                    "changes": {
                        "group": {
                            "created": groups_created,
                            "maintained": groups_maintained,
                            "failed": groups_failed,
                        },
                        "subject": {
                            "created": subjects_created,
                            "maintained": subject_maintained,
                            "failed": subjects_failed,
                        },
                    },
                },
                "is_done": False,
            }

    yield {
        "result": {
            "entity": "group",
            "action": "import",
            "errors": errors,
            "changes": {
                "group": {
                    "created": groups_created,
                    "maintained": groups_maintained,
                    "failed": groups_failed,
                },
                "subject": {
                    "created": subjects_created,
                    "maintained": subject_maintained,
                    "failed": subjects_failed,
                },
            },
        },
        "is_done": True,
    }


def ensure_group_exists(group_data, group_type, subject=None):
    """
    Ensure a group exists, maintaining it if it already exists or creating it if not.
    Returns (group, created_bool, error_message)
    """
    feide_id = group_data["id"]

    # Check if group already exists
    existing_group = models.Group.objects.filter(feide_id__exact=feide_id).first()
    if existing_group:
        existing_group.display_name = group_data["displayName"]
        existing_group.subject = subject
        existing_group.valid_from = group_data.get("notBefore")
        existing_group.valid_to = group_data.get("notAfter")
        existing_group.maintained_at = timezone.now()
        existing_group.save()
        print("Maintained group:", feide_id)
        return existing_group, False, None

    # For a new group, ensure the parent school exists
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
        return None, False, f"Failed to create group {feide_id}: {str(error)[:1000]}"


def ensure_subject_exists(grep_code):
    """
    Ensure a subject exists in the database, fetching from UDIR if necessary.
    Returns (subject, created_bool, error_message)
    """
    # Check if subject already exists
    existing_subject = models.Subject.objects.filter(grep_code__exact=grep_code).first()
    if existing_subject:
        existing_subject.maintained_at = timezone.now()
        existing_subject.save()
        return existing_subject, False, None

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
            return subject, True, None
        else:
            return None, False, f"UDIR API returned status {
                udir_response.status_code}  for grep code {grep_code} "

    except Exception as error:
        return None, False, f"Failed to fetch subject from UDIR for grep code {grep_code}: {
            str(error)[: 1000]} "
