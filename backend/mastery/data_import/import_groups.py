import os
import json
from django.utils import timezone
import requests
from mastery import models
import logging

UDIR_GREP_URL = os.environ.get('UDIR_GREP_URL')

logger = logging.getLogger(__name__)


# Get data directory path
script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, "data")


def import_groups_from_file(org_number):
    """Import groups for ONE school from data_import/data/schools/<org>/groups.json"""
    logger.debug("Starting group import for organization: %s", org_number)

    school = models.School.objects.filter(org_number=org_number).first()
    if not school:
        logger.error("School with org number %s not found in database.", org_number)
        raise Exception(f"School with org number {org_number} not found in database.")

    groups_file = os.path.join(data_dir, org_number, "groups.json")
    if not os.path.exists(groups_file):
        logger.error("Groups file not found for school %s at path: %s", org_number, groups_file)
        raise Exception(
            f"Groups file not found for school {org_number}. Fetch groups first."
        )

    with open(groups_file, "r", encoding="utf-8") as file:
        groups_data = json.load(file)

    # Progress reporting variables
    basis_group_created = 0
    basis_group_maintained = 0
    teaching_group_created = 0
    teaching_group_maintained = 0
    subjects_created = 0
    subject_maintained = 0
    subjects_failed = 0
    errors = []

    basis_groups = groups_data.get("basis", [])
    teaching_groups = groups_data.get("teaching", [])

    # Handle basis groups
    for index, group_data in enumerate(basis_groups):
        _, created = ensure_group_exists(group_data, "basis", None)
        if created:
            basis_group_created += 1
        else:
            basis_group_maintained += 1

        if index % 10 == 0:
            yield {
                "result": {
                    "entity": "group",
                    "action": "import",
                    "errors": errors,
                    "changes": {
                        "basis_group": {
                            "created": basis_group_created,
                            "maintained": basis_group_maintained,
                        },
                        "teaching_group": {
                            "created": teaching_group_created,
                            "maintained": teaching_group_maintained,
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
    for index, group_data in enumerate(teaching_groups):
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

        _, created = ensure_group_exists(group_data, "teaching", subject)
        if created:
            teaching_group_created += 1
        else:
            teaching_group_maintained += 1

        if index % 10 == 0:
            yield {
                "result": {
                    "entity": "group",
                    "action": "import",
                    "errors": errors,
                    "changes": {
                        "basis_group": {
                            "created": basis_group_created,
                            "maintained": basis_group_maintained,
                        },
                        "teaching_group": {
                            "created": teaching_group_created,
                            "maintained": teaching_group_maintained,
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
                "basis_group": {
                    "created": basis_group_created,
                    "maintained": basis_group_maintained,
                },
                "teaching_group": {
                    "created": teaching_group_created,
                    "maintained": teaching_group_maintained,
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
    Returns (group, created_bool)
    """
    feide_id = group_data["id"]
    now = timezone.now()
    # Check if group already exists
    existing_group = models.Group.objects.filter(feide_id__exact=feide_id).first()
    if existing_group:
        # Do not touch the is_enabled field on existing groups
        # Do not touch the type field on existing groups
        # Unset deleted_at (in case it was set)
        existing_group.display_name = group_data["displayName"]
        existing_group.subject = subject
        existing_group.valid_from = group_data.get("notBefore")
        existing_group.valid_to = group_data.get("notAfter")
        existing_group.maintained_at = now
        existing_group.save()
        if existing_group.deleted_at:
            existing_group.deleted_at = None
            # Cascade unset any soft-delete timestamp on related goals
            models.Goal.objects.filter(
                group=existing_group).update(
                maintained_at=now, deleted_at=None)
        logger.debug("Maintained existing group: %s", feide_id)
        return existing_group, False

    # For a new group, ensure the parent school exists
    school = models.School.objects.filter(feide_id__exact=group_data["parent"]).first()

    new_group = models.Group.objects.create(
        display_name=group_data["displayName"],
        type=group_type,
        school=school,
        subject=subject,
        feide_id=feide_id,
        valid_from=group_data.get("notBefore"),
        valid_to=group_data.get("notAfter"),
        maintained_at=now,
    )
    logger.debug("Created new group: %s", feide_id)
    return new_group, True


def ensure_subject_exists(grep_code):
    """
    Ensure a subject exists in the database, fetching from UDIR if necessary.
    Returns (subject, created_bool)
    """
    # Check if subject already exists
    existing_subject = models.Subject.objects.filter(grep_code__exact=grep_code).first()
    if existing_subject:
        existing_subject.maintained_at = timezone.now()
        existing_subject.save(update_fields=['maintained_at'])
        return existing_subject, False, None

    udir_response = requests.get(f"{UDIR_GREP_URL}/{grep_code}")

    if udir_response.status_code == 200:
        udir_subject = udir_response.json()
        display_name = udir_subject.get('tittel', [{}])[0].get('verdi')
        short_name = udir_subject.get('kortform', [{}])[0].get('verdi')
        grep_group_code = udir_subject['opplaeringsfag'][0]['kode'] if udir_subject.get(
            'opplaeringsfag') and len(udir_subject['opplaeringsfag']) > 0 else None

        subject = models.Subject.objects.create(
            display_name=display_name,
            short_name=short_name,
            grep_code=grep_code,
            grep_group_code=grep_group_code,
            maintained_at=timezone.now(),
        )
        logger.debug("Created new subject: %s (%s)", grep_code, display_name)
        return subject, True, None
    else:
        message = f"UDIR http trouble: {udir_response.status_code} for grep_code {grep_code}"
        logger.warning(message)
        return None, False, message
