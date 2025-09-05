import os
import json
from django.utils import timezone
from mastery import models
from .feide_api import ensure_subject

# Get data directory path
script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, "data")


def import_groups_from_file(
    org_number, is_overwrite_enabled=False
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

    stats = import_groups_from_data(
        groups,
        is_overwrite_enabled=is_overwrite_enabled,
    )
    print("✅ import_groups_from_file COMPLETED")
    return stats


def import_groups_from_data(
    groups_data, is_overwrite_enabled=False
):
    """Import both basis and teaching groups from provided data"""
    stats = {
        "basis_groups_created": 0,
        "basis_groups_existing": 0,
        "basis_groups_updated": 0,
        "teaching_groups_created": 0,
        "teaching_groups_existing": 0,
        "teaching_groups_updated": 0,
        "subjects_created": 0,
        "subjects_existing": 0,
        "groups_without_subjects": 0,
        "groups_with_subjects": 0,
    }

    import_basis_groups(
        groups_data.get("basis", []), stats, is_overwrite_enabled
    )
    import_teaching_groups(
        groups_data.get("teaching", []), stats, is_overwrite_enabled)
    return stats


def import_basis_groups(
    basis_groups, stats, is_overwrite_enabled=False
):
    """Import basis groups from groups data"""
    print(f"\n👥 Basis groups: {len(basis_groups)}")
    for group in basis_groups:
        group_obj, created, error=ensure_group_exists(
            group, "basis", None, is_overwrite_enabled
        )
        if error:
            print(f"  ❌ {error}")
            continue
        if created:
            print(f"  ✅ Basis group created: {group_obj.display_name}")
            stats["basis_groups_created"] += 1
        else:
            if is_overwrite_enabled:
                print(f"  🔄 Basis group updated: {group_obj.display_name}")
                stats["basis_groups_updated"] += 1
            else:
                print(f"  📋 Basis group already exists: {group_obj.display_name}")
                stats["basis_groups_existing"] += 1


def import_teaching_groups(
    teaching_groups, stats, is_overwrite_enabled=False):
    """Import teaching groups from groups data"""
    print(f"\n📚 Teaching groups: {len(teaching_groups)}")
    for group in teaching_groups:
        subject=process_subject_for_group(group, stats)
        group_obj, created, error=ensure_group_exists(
            group, "teaching", subject, is_overwrite_enabled
        )
        if error:
            print(f"  ❌ {error}")
            continue
        if created:
            print(f"  ✅ Teaching group created: {group_obj.display_name}")
            stats["teaching_groups_created"] += 1
        else:
            if is_overwrite_enabled:
                print(f"  🔄 Teaching group updated: {group_obj.display_name}")
                stats["teaching_groups_updated"] += 1
            else:
                print(f"  📋 Teaching group already exists: {group_obj.display_name}")
                stats["teaching_groups_existing"] += 1


def ensure_group_exists(
    group_data,
    group_type,
    subject=None,
    is_overwrite_enabled=False,
):
    """
    Create-or-update any group type.
    Returns (group, created_bool, error_message)
    """
    feide_id=group_data["id"]

    # Check if group already exists
    existing_group=models.Group.objects.filter(feide_id__exact=feide_id).first()
    if existing_group:
        if is_overwrite_enabled:
            existing_group.display_name=group_data["displayName"]
            existing_group.subject=subject
            existing_group.valid_from=group_data.get("notBefore")
            existing_group.valid_to=group_data.get("notAfter")
            existing_group.maintained_at=timezone.now()
            existing_group.save()
        else:
            return existing_group, False, None

    # Find parent school
    school=models.School.objects.filter(feide_id__exact=group_data["parent"]).first()
    if not school:
        return None, False, f"School not found for group {feide_id}"

    try:
        new_group=models.Group.objects.create(
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
        error_message=f"Failed to create group {feide_id}: {str(e)}"
        return None, False, error_message


def process_subject_for_group(group_data, stats):
    """
    Handle subject processing for teaching groups
    Returns subject object or None
    """
    if "grep" not in group_data or "code" not in group_data["grep"]:
        stats["groups_without_subjects"] += 1
        print(f"  ⚠️ No subject code for: {group_data['displayName']}")
        return None

    grep_code=group_data["grep"]["code"]

    existing_subject=models.Subject.objects.filter(grep_code__exact=grep_code).first()
    if existing_subject:
        stats["subjects_existing"] += 1
        print(f"  📖 Subject exists: {existing_subject.display_name}")
        stats["groups_with_subjects"] += 1
        return existing_subject

    subject=ensure_subject(grep_code)
    if subject:
        stats["subjects_created"] += 1
        print(
            f"  ✨ Subject created: {subject.display_name}"
        )
        stats["groups_with_subjects"] += 1
        return subject

    stats["groups_without_subjects"] += 1
    return None
