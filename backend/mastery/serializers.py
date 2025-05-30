from rest_framework import serializers
from mastery import models
from django.db.models import ForeignKey

# Base serializer that rewrites foreign key fields
class BaseModelSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # On incoming data, for every FK on this model, `<fk_name>_id`
        for field in self.Meta.model._meta.get_fields():
            if isinstance(field, ForeignKey):
                name = field.name
                qs   = field.remote_field.model.objects.all()
                self.fields[f"{name}_id"] = serializers.PrimaryKeyRelatedField(
                    source=name,
                    queryset=qs,
                    write_only=True,
                    required= not field.null
                )
    
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

# Base serializers for UserGroup and StatusGoal
class UserGroupSerializer(BaseModelSerializer):
    class Meta:
        model = models.UserGroup
        fields = '__all__'

# Basic serializers (without nested relationships)
class SchoolSerializer(BaseModelSerializer):
    class Meta:
        model = models.School
        fields = '__all__'

class SubjectSerializer(BaseModelSerializer):
    class Meta:
        model = models.Subject
        fields = '__all__'

class RoleSerializer(BaseModelSerializer):
    class Meta:
        model = models.Role
        fields = '__all__'

# Nested serializers
class BasicUserSerializer(BaseModelSerializer):
    """Basic user serializer without nested relationships to avoid circular references"""
    class Meta:
        model = models.User
        fields = '__all__'

class BasicGroupSerializer(BaseModelSerializer):
    """Basic group serializer without nested relationships to avoid circular references"""
    class Meta:
        model = models.Group
        fields = '__all__'

class BasicGoalSerializer(BaseModelSerializer):
    """Basic goal serializer without nested relationships to avoid circular references"""
    class Meta:
        model = models.Goal
        fields = '__all__'

class BasicStatusSerializer(BaseModelSerializer):
    """Basic status serializer without nested relationships to avoid circular references"""
    class Meta:
        model = models.Status
        fields = '__all__'

class BasicSituationSerializer(BaseModelSerializer):
    """Basic situation serializer without nested relationships to avoid circular references"""
    class Meta:
        model = models.Situation
        fields = '__all__'

# Nested UserGroup serializer for use in User and Group serializers
class NestedUserGroupSerializer(BaseModelSerializer):
    role = RoleSerializer(read_only=True)
    
    class Meta:
        model = models.UserGroup
        exclude = ('user',)  # Exclude user when used within User serializer
        
class NestedGroupUserSerializer(BaseModelSerializer):
    role = RoleSerializer(read_only=True)
    user = BasicUserSerializer(read_only=True)
    
    class Meta:
        model = models.UserGroup
        exclude = ('group',)  # Exclude group when used within Group serializer

# Main serializers with relationships
class UserSerializer(BaseModelSerializer):
    groups = NestedUserGroupSerializer(source='usergroup_set', many=True, read_only=True)
    
    class Meta:
        model = models.User
        fields = '__all__'

class GroupSerializer(BaseModelSerializer):
    members = NestedGroupUserSerializer(source='usergroup_set', many=True, read_only=True)
    
    class Meta:
        model = models.Group
        fields = '__all__'

class GoalSerializer(BaseModelSerializer):
    class Meta:
        model = models.Goal
        fields = '__all__'

class SituationSerializer(BaseModelSerializer):
    class Meta:
        model = models.Situation
        fields = '__all__'

class ObservationSerializer(BaseModelSerializer):
    # nest all FK relations for read
    goal = BasicGoalSerializer(read_only=True)
    student = BasicUserSerializer(read_only=True)
    observer = BasicUserSerializer(read_only=True)
    situation = BasicSituationSerializer(read_only=True)

    class Meta:
        model = models.Observation
        fields = '__all__'

class StatusSerializer(BaseModelSerializer):    
    class Meta:
        model = models.Status
        fields = '__all__'