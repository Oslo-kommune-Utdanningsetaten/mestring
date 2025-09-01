
from django.utils import timezone
from .feide_api import fetch_school_group
from .helpers import get_feide_access_token
from mastery import models


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
    
    return {
        "status": "created" if created else "updated",
        "org_number": school.org_number,
        "display_name": school.display_name,
        "feide_id": school.feide_id,
    }


