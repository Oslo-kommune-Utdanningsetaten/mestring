
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
                    "entity": "school",
                    "action": "update",
                    "total_count": iterations,
                    "success_count": success_count,
                    "failure_count": failure_count,
                    "errors": errors,
                },
                "is_done": index == iterations,
            }


def import_school_from_feide(org_number):
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
    ensure_default_mastery_schema_exists(school)
    return {
        "status": "created" if created else "updated",
        "org_number": school.org_number,
        "display_name": school.display_name,
        "feide_id": school.feide_id,
    }


def ensure_default_mastery_schema_exists(school):
    mastery_schema = models.MasterySchema.objects.filter(school_id=school.id).first()
    if mastery_schema:
        return mastery_schema

    return models.MasterySchema.objects.create(
        title='Mestringstrappa',
        description='Mestring angitt med fem nivåer, fra "aldri" til "mestrer".',
        school=school,
        maintained_at=timezone.now(),
        config={
            "levels": [
                {
                    "text": "Mestrer ikke",
                    "color": "rgb(229, 50, 43)",
                    "maxValue": 20,
                    "minValue": 1
                },
                {
                    "text": "Mestrer sjelden",
                    "color": "rgb(159, 113, 202)",
                    "maxValue": 40,
                    "minValue": 21
                },
                {
                    "text": "Mestrer iblant",
                    "color": "rgb(86, 174, 232)",
                    "maxValue": 60,
                    "minValue": 41
                },
                {
                    "text": "Mestrer ofte",
                    "color": "rgb(241, 249, 97)",
                    "maxValue": 80,
                    "minValue": 61
                },
                {
                    "text": "Mestrer",
                    "color": "rgb(160, 207, 106)",
                    "maxValue": 100,
                    "minValue": 81
                }
            ],
            "inputIncrement": 1,
            "renderDirection": "vertical",
            "isTitleInputEnabled": True,
            "isColorGradientEnabled": False,
            "isFeedforwardInputEnabled": True,
            "isMasteryValueInputEnabled": True,
            "isIncrementIndicatorEnabled": True,
            "isMasteryDescriptionInputEnabled": True
        }
    )
