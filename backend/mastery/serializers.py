from rest_framework import serializers
from mastery import models
from django.db.models import ForeignKey, ManyToManyField
from mastery.access_policies.observation import ObservationAccessPolicy


class BaseModelSerializer(serializers.ModelSerializer):
    READ_ONLY_BASE_FIELDS = (
        'id',
        'created_at',
        'updated_at',
        'maintained_at',
    )

    READ_ONLY_FK_FIELDS = (
        'created_by',
        'updated_by',
    )

    # Fields override, used for renaming foreign key fields
    def get_fields(self):
        fields = super().get_fields()

        # Get explicitly declared fields from the serializer class
        declared_fields = getattr(self.Meta, 'fields', [])
        explicitly_nested_fields = set()

        # Check for explicitly declared nested serializers
        for field_name, field_instance in self._declared_fields.items():
            if isinstance(field_instance, serializers.ModelSerializer):
                explicitly_nested_fields.add(field_name)

        # Rename FK ID fields
        for field in self.Meta.model._meta.get_fields():
            original_field_name = field.name

            # Skip rename if this field is explicitly declared as nested
            if original_field_name in explicitly_nested_fields:
                continue
            # Skip rename if the field is not in the serializer fields
            if not original_field_name in fields:
                continue

            # Rename FK ID field (e.g. student --> student_id)
            if isinstance(field, ForeignKey):
                # Remove original field
                del fields[original_field_name]
                new_field_name = f"{original_field_name}_id"

                if original_field_name in self.READ_ONLY_FK_FIELDS:
                    fields[new_field_name] = serializers.PrimaryKeyRelatedField(
                        source=original_field_name,
                        read_only=True
                    )
                else:
                    request = self.context.get('request')
                    # Ensure access policy is applied to the related field queryset
                    qs = field.remote_field.model.objects.all()
                    policy_class = getattr(field.remote_field.model, 'access_policy', None)
                    if request and policy_class:
                        policy = policy_class()
                        qs = policy.scope_queryset(request, qs)
                    fields[new_field_name] = serializers.PrimaryKeyRelatedField(
                        source=original_field_name,
                        queryset=qs,
                        required=not field.null,
                        allow_null=field.null
                    )

            # Rename many-to-many FK ID field (e.g. groups --> group_ids)
            if isinstance(field, ManyToManyField):
                # Remove original field
                del fields[original_field_name]
                new_field_name = original_field_name

                # remove pluralization if present
                if new_field_name.endswith('s'):
                    new_field_name = new_field_name[:-1]

                # Add the new field with '_ids' suffix
                new_field_name = f"{new_field_name}_ids"
                fields[new_field_name] = serializers.PrimaryKeyRelatedField(
                    source=original_field_name,
                    many=True,
                    read_only=True,
                )

        # Ensure base model metadata fields are read-only when present
        for field_name in self.READ_ONLY_BASE_FIELDS:
            if field_name in fields:
                fields[field_name].read_only = True

        for field_name in self.READ_ONLY_FK_FIELDS:
            lookup_name = f"{field_name}_id"
            if lookup_name in fields:
                fields[lookup_name].read_only = True
        return fields


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
        fields['is_individual'] = serializers.BooleanField(read_only=True)
        return fields


class SituationSerializer(BaseModelSerializer):
    class Meta:
        model = models.Situation
        fields = '__all__'


class ObservationSerializer(BaseModelSerializer):
    class Meta:
        model = models.Observation
        fields = '__all__'

    def validate(self, attrs):
        goal = attrs.get('goal')  # in case of create
        if goal is None and self.instance:
            goal = self.instance.goal  # in case of partial update

        mastery_value = attrs.get('mastery_value')

        if goal and mastery_value is not None:
            if not goal.mastery_schema:
                return attrs

            schema_min, schema_max = goal.mastery_schema.get_value_range()
            if schema_min is None or schema_max is None:
                return attrs

            if mastery_value < schema_min or mastery_value > schema_max:
                raise serializers.ValidationError(
                    {'mastery_value': f'Must be between {schema_min} and {schema_max}'}
                )

        return attrs


class GoalWithObservationsSerializer(GoalSerializer):
    observations = serializers.SerializerMethodField()

    class Meta(GoalSerializer.Meta):
        pass

    def get_observations(self, goal):
        request = self.context.get('request')
        if not request:
            raise ValueError("GoalWithObservationsSerializer requires request in context")

        # Start with access-policy-filtered observations
        policy = ObservationAccessPolicy()
        observations_qs = policy.scope_queryset(request, models.Observation.objects.all())

        # Filter to this goal's observations
        observations_qs = observations_qs.filter(goal_id=goal.id)

        # Filter by student if provided
        student_id = request.query_params.get('student')
        if student_id:
            observations_qs = observations_qs.filter(student_id=student_id)

        # Serialize the filtered observations
        return ObservationSerializer(observations_qs, many=True, context=self.context).data


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
