from rest_framework import serializers
from mastery import models
from django.db.models import ForeignKey
from mastery.access_policies.observation import ObservationAccessPolicy


class BaseModelSerializer(serializers.ModelSerializer):
    # Base serializer that rewrites foreign key fields
    def get_fields(self):
        fields = super().get_fields()

        # Get explicitly declared fields from the serializer class
        declared_fields = getattr(self.Meta, 'fields', [])
        explicitly_nested_fields = set()

        # Check for explicitly declared nested serializers
        for field_name, field_instance in self._declared_fields.items():
            if isinstance(field_instance, serializers.ModelSerializer):
                explicitly_nested_fields.add(field_name)

        # Add FK ID fields and remove original FK fields
        for field in self.Meta.model._meta.get_fields():
            if isinstance(field, ForeignKey):
                name = field.name

                # Skip conversion if this field is explicitly declared as nested
                if name in explicitly_nested_fields:
                    continue

                qs = field.remote_field.model.objects.all()
                # Add the ID field
                fields[f"{name}_id"] = serializers.PrimaryKeyRelatedField(
                    source=name,
                    queryset=qs,
                    required=not field.null,
                    allow_null=field.null
                )
                # Remove the original field to avoid duplication
                if name in fields:
                    del fields[name]
        return fields

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # On outgoing data, rename all FK fields `foo` → `fooId`
        for field in self.Meta.model._meta.get_fields():
            if isinstance(field, ForeignKey) and field.name in data:
                val = data[field.name]
                # only rename if it's not already a nested dict/list
                if not isinstance(val, (dict, list)):
                    data[f"{field.name}Id"] = data.pop(field.name)
        return data


class SubjectSerializer(BaseModelSerializer):
    class Meta:
        model = models.Subject
        fields = '__all__'


class RoleSerializer(BaseModelSerializer):
    class Meta:
        model = models.Role
        fields = '__all__'


class UserSerializer(BaseModelSerializer):
    class Meta:
        model = models.User
        fields = '__all__'


class GroupSerializer(BaseModelSerializer):
    class Meta:
        model = models.Group
        fields = '__all__'


class GoalSerializer(BaseModelSerializer):
    class Meta:
        model = models.Goal
        fields = '__all__'

    def get_fields(self):
        fields = super().get_fields()
        # Add computed/property fields
        fields['is_personal'] = serializers.BooleanField(read_only=True)
        return fields


class SituationSerializer(BaseModelSerializer):
    class Meta:
        model = models.Situation
        fields = '__all__'


class ObservationSerializer(BaseModelSerializer):
    class Meta:
        model = models.Observation
        fields = '__all__'


class StatusSerializer(BaseModelSerializer):
    class Meta:
        model = models.Status
        fields = '__all__'


class SchoolSerializer(BaseModelSerializer):
    class Meta:
        model = models.School
        fields = '__all__'


class MasterySchemaSerializer(BaseModelSerializer):
    class Meta:
        model = models.MasterySchema
        fields = '__all__'


class UserSchoolSerializer(BaseModelSerializer):
    class Meta:
        model = models.UserSchool
        fields = '__all__'


class UserGroupSerializer(BaseModelSerializer):
    class Meta:
        model = models.UserGroup
        fields = '__all__'


class NestedUserGroupSerializer(BaseModelSerializer):
    user = UserSerializer(read_only=True)
    group = GroupSerializer(read_only=True)
    role = RoleSerializer(read_only=True)

    class Meta:
        model = models.UserGroup
        fields = '__all__'


class NestedUserSchoolSerializer(BaseModelSerializer):
    user = UserSerializer(read_only=True)
    school = SchoolSerializer(read_only=True)
    role = RoleSerializer(read_only=True)

    class Meta:
        model = models.UserSchool
        fields = '__all__'


class DataMaintenanceTaskSerializer(BaseModelSerializer):
    class Meta:
        model = models.DataMaintenanceTask
        fields = '__all__'


class DataMaintenanceTaskSerializer(BaseModelSerializer):
    class Meta:
        model = models.DataMaintenanceTask
        fields = '__all__'
