
from django.utils import timezone
from .feide_api import fetch_school_group
from .helpers import get_feide_access_token
from mastery import models
import time


# This function simulates updating school names in chunks, yielding progress updates
def school_update(org_number: str):

    school, _ = models.School.objects.get_or_create(
        org_number=org_number,
        defaults={
            "display_name": 'Kakrafoon School',
            "feide_id": f"fc:org:feide.osloskolen.no:unit:{org_number}",
            "maintained_at": timezone.now(),
            "owner": 'fc:org:feide.osloskolen.no',
        },
    )
    success_count = 0
    failure_count = 0
    errors = []

    iterations = 1000
    chunk_size = 10

    for index in range(1, iterations + 1):
        new_name = f'Kakrafoon School {index}'
        school.display_name = new_name

        try:
            # Simulate occasional failure if we want to
            should_fail = False
            if should_fail:
                raise RuntimeError("Simulated update failure")

            school.save()
            success_count += 1
        except Exception as error:
            failure_count += 1
            errors.append({
                "error": "update-error",
                "message": f"Unable to update school with id {school.id}, name {new_name}. Reason: {str(error)[:1000]}",
            })

        # Yield result at every chunk_size iteration or at the end
        if index % chunk_size == 0 or index == iterations:
            yield {
                "result": {
                    "key": "school-update",
                    "entity": "school",
                    "action": "update",
                    "total_count": iterations,
                    "success_count": success_count,
                    "failure_count": failure_count,
                    "errors": errors,
                },
                "is_done": index == iterations,
            }


def import_school_from_feide(org_number, is_overwrite_enabled=False, is_crash_on_error_enabled=False):
    """import a single school by org number from Feide and create/update in our database."""

    token = get_feide_access_token()
    school_data = fetch_school_group(org_number, token)

    if not school_data:
        return {"status": "not_found", "org_number": org_number}

    feide_id = school_data.get('id')
    display_name = school_data.get('displayName')
    owner = school_data.get('parent')
    if not feide_id or not display_name:
        raise Exception(f"Invalid school data from Feide for org {org_number}")

    school, created = models.School.objects.update_or_create(
        org_number=org_number,
        defaults={
            "display_name": display_name,
            "feide_id": feide_id,
            "maintained_at": timezone.now(),
            "owner": owner,
        },
    )

    return {
        "status": "created" if created else "updated",
        "org_number": school.org_number,
        "display_name": school.display_name,
        "feide_id": school.feide_id,
    }
