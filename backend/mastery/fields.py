import json

from django.db import models


class PlainJSONField(models.JSONField):
    """JSONField that stores as PostgreSQL json (not jsonb) to preserve key order."""

    def db_type(self, connection):
        return "json"

    def get_internal_type(self):
        return "PlainJSONField"

    # Bypass automatic JSON decoding Django performs on JSONField data
    # psycopg2 already decodes json columns into Python objects
    def from_db_value(self, value, expression, connection):
        return value

    def get_db_prep_value(self, value, connection, prepared=False):
        # Django's JSONField wraps values in a Jsonb adapter that sorts keys.
        # Serialize to a plain string here so the raw JSON text is sent to Postgres.
        if isinstance(value, (dict, list)):
            value = json.dumps(value, cls=self.encoder)
        return value
