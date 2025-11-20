from django.utils import timezone
from mastery import models
import logging
logger = logging.getLogger(__name__)


def do_stuff(org_number, last_maintained_before):
    logger.debug("TBA %s", org_number)
