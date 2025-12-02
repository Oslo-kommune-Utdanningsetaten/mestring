from django.db import models
from django.db.models import Q
from django.utils import timezone


class GroupQuerySet(models.QuerySet):
    def within_validity_period(self):
        """
        Filter groups currently within their validity period
        - valid_from is null or <= now
        - valid_to is null or >= now
        """
        now = timezone.now()
        return self.filter(
            Q(valid_from__isnull=True) | Q(valid_from__lte=now)
        ).filter(
            Q(valid_to__isnull=True) | Q(valid_to__gte=now)
        )

    def outside_validity_period(self):
        """
        Filter groups currently outside their validity period
        - valid_from is in the future, OR
        - valid_to is in the past
        """
        now = timezone.now()
        return self.filter(
            Q(valid_from__gt=now) | Q(valid_to__lt=now)
        )
