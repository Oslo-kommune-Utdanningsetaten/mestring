import os
import json
from django.utils import timezone
import requests
from mastery import models

UDIR_GREP_URL = os.environ.get('UDIR_GREP_URL')

# Get data directory path
script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, "data")


def import_groups_from_file(
    org_number, is_overwrite_enabled=False, is_crash_on_error_enabled=False
):
    """Import groups for ONE school from imports/data/schools/<org>/groups.json"""
    print("👉 import_groups_from_file: BEGIN")

    groups_file = os.path.join(data_dir, org_number, "groups.json")
    if not os.path.exists(groups_file):
        raise Exception(
            f"Groups file not found for school {org_number}. Fetch groups first."
        )

    with open(groups_file, "r") as file:
        groups_data = json.load(file)

    groups = {
        "basis": groups_data.get("basis", []) or [],
        "teaching": groups_data.get("teaching", []) or [],
    }

    stats = process_groups_data(
        groups,
        is_overwrite_enabled=is_overwrite_enabled,
    )
    print("✅ import_groups_from_file COMPLETED")
    return stats


def process_groups_data(groups_data, is_overwrite_enabled=False):
    """Import both basis and teaching groups from provided data"""

    # Call functions and get their results
    basis_stats = import_basis_groups(
        groups_data.get("basis", []), is_overwrite_enabled
    )
    teaching_stats = import_teaching_groups(
        groups_data.get("teaching", []), is_overwrite_enabled
    )

    all_errors = basis_stats["errors"] + teaching_stats["errors"]
    # Combine results explicitly
    combined_stats = {
        "basis_groups_created": basis_stats["groups_created"],
        "basis_groups_existing": basis_stats["groups_existing"],
        "basis_groups_updated": basis_stats["groups_updated"],

        "teaching_groups_created": teaching_stats["groups_created"],
        "teaching_groups_existing": teaching_stats["groups_existing"],
        "teaching_groups_updated": teaching_stats["groups_updated"],

        "subjects_created": teaching_stats["subjects_created"],
        "subjects_existing": teaching_stats["subjects_existing"],
        "groups_without_subjects": teaching_stats["groups_without_subjects"],
        "groups_with_subjects": teaching_stats["groups_with_subjects"],
        
        "errors": all_errors,
        "total_errors": len(all_errors)
    }

    return combined_stats


def import_basis_groups(basis_groups, is_overwrite_enabled=False, is_crash_on_error_enabled=False):
    """Import basis groups from groups data"""
    print(f"\n👥 Basis groups: {len(basis_groups)}")

    stats = {
        "groups_created": 0,
        "groups_existing": 0,
        "groups_updated": 0,
        "errors": []
    }

    for group in basis_groups:
        group_obj, created, error = ensure_group_exists(
            group, "basis", None, is_overwrite_enabled
        )
        if error:
            stats["errors"].append({
                "name": group.get("displayName"),
                "message": error
            })
            print(f"  ❌ {error}")
            if is_crash_on_error_enabled:
                raise Exception(f"Import stopped: {error}")
            continue
        if created:
            print(f"  ✅ Basis group created: {group_obj.display_name}")
            stats["groups_created"] += 1
        else:
            if is_overwrite_enabled:
                print(f"  🔄 Basis group updated: {group_obj.display_name}")
                stats["groups_updated"] += 1
            else:
                print(f"  📋 Basis group already exists: {group_obj.display_name}")
                stats["groups_existing"] += 1

    return stats


def import_teaching_groups(teaching_groups, is_overwrite_enabled=False, is_crash_on_error_enabled=False):
    """Import teaching groups from groups data"""
    print(f"\n📚 Teaching groups: {len(teaching_groups)}")

    stats = {
        "groups_created": 0,
        "groups_existing": 0,
        "groups_updated": 0,
        "subjects_created": 0,
        "subjects_existing": 0,
        "groups_without_subjects": 0,
        "groups_with_subjects": 0,
        "errors": []
    }

    for group in teaching_groups:
        # Process subject and get its stats
        subject = None
        if "grep" in group and "code" in group["grep"]:
            grep_code = group["grep"]["code"]
            subject, subject_was_created = ensure_subject(grep_code)
            
            if subject:
                if subject_was_created:
                    stats["subjects_created"] += 1
                    print(f"  ✨ Subject created: {subject.display_name}")
                else:
                    stats["subjects_existing"] += 1
                    print(f"  📖 Subject exists: {subject.display_name}")
                stats["groups_with_subjects"] += 1
            else:
                stats["groups_without_subjects"] += 1
                print(f"  ⚠️ No subject found for code: {grep_code}")
        else:
            stats["groups_without_subjects"] += 1
            print(f"  ⚠️ No subject code for: {group['displayName']}")

        group_obj, created, error = ensure_group_exists(
            group, "teaching", subject, is_overwrite_enabled
        )
        if error:
            stats["errors"].append({
                "name": group.get("displayName"),
                "message": error
            })
            if is_crash_on_error_enabled:
                raise Exception(f"Import stopped: {error}")
            continue

        if created:
            print(f"  ✅ Teaching group created: {group_obj.display_name}")
            stats["groups_created"] += 1
        else:
            if is_overwrite_enabled:
                print(f"  🔄 Teaching group updated: {group_obj.display_name}")
                stats["groups_updated"] += 1
            else:
                print(f"  📋 Teaching group already exists: {group_obj.display_name}")
                stats["groups_existing"] += 1

    return stats


def ensure_group_exists(
    group_data,
    group_type,
    subject=None,
    is_overwrite_enabled=False,
    is_crash_on_error_enabled=False,
):
    """
    Create-or-update any group type.
    Returns (group, created_bool, error_message)
    """
    feide_id = group_data["id"]

    # Check if group already exists
    existing_group = models.Group.objects.filter(feide_id__exact=feide_id).first()
    if existing_group and is_overwrite_enabled:
        existing_group.display_name = group_data["displayName"]
        existing_group.subject = subject
        existing_group.valid_from = group_data.get("notBefore")
        existing_group.valid_to = group_data.get("notAfter")
        existing_group.maintained_at = timezone.now()
        existing_group.save()

    if existing_group:
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
        return new_group, True, None

    except Exception as e:
        error_message = f"Failed to create group {feide_id}: {str(e)}"
        return None, False, error_message


def ensure_subject(grep_code):
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

            print("  Creating subject:", grep_code, display_name)
            subject = models.Subject.objects.create(
                display_name=display_name,
                short_name=short_name,
                grep_code=grep_code,
                grep_group_code=grep_group_code,
                maintained_at=timezone.now(),
            )

            return subject, True
    except Exception as e:
        print("🚷Failed to fetch subject from UDIR:", {str(e)})
        return None, False
        
