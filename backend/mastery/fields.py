from django.db import models


class PlainJSONField(models.JSONField):
    """JSONField that stores as PostgreSQL json (not jsonb) to preserve key order."""

    def db_type(self, connection):
        if connection.vendor == "postgresql":
            return "json"
        return super().db_type(connection)

    def get_internal_type(self):
        return "PlainJSONField"
