from rest_framework import serializers
from mastery import models

# This file contains the serializers for the models in the mastery app.
# Except UserGroup and StatusGoal, how do we deal with these?

# Base serializers for UserGroup and StatusGoal
class UserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserGroup
        fields = '__all__'

class StatusGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StatusGoal
        fields = '__all__'

# Basic serializers (without nested relationships)
class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.School
        fields = '__all__'

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Subject
        fields = '__all__'

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Role
        fields = '__all__'

# Nested serializers
class BasicUserSerializer(serializers.ModelSerializer):
    """Basic user serializer without nested relationships to avoid circular references"""
    class Meta:
        model = models.User
        fields = '__all__'

class BasicGroupSerializer(serializers.ModelSerializer):
    """Basic group serializer without nested relationships to avoid circular references"""
    class Meta:
        model = models.Group
        fields = '__all__'

class BasicGoalSerializer(serializers.ModelSerializer):
    """Basic goal serializer without nested relationships to avoid circular references"""
    class Meta:
        model = models.Goal
        fields = '__all__'

class BasicStatusSerializer(serializers.ModelSerializer):
    """Basic status serializer without nested relationships to avoid circular references"""
    class Meta:
        model = models.Status
        fields = '__all__'

# Nested UserGroup serializer for use in User and Group serializers
class NestedUserGroupSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    
    class Meta:
        model = models.UserGroup
        exclude = ('user',)  # Exclude user when used within User serializer
        
class NestedGroupUserSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    user = BasicUserSerializer(read_only=True)
    
    class Meta:
        model = models.UserGroup
        exclude = ('group',)  # Exclude group when used within Group serializer

# Nested StatusGoal serializer for use in Status serializer
class NestedStatusGoalSerializer(serializers.ModelSerializer):
    goal = BasicGoalSerializer(read_only=True)
    
    class Meta:
        model = models.StatusGoal
        exclude = ('status',)  # Exclude status when used within Status serializer

# Main serializers with relationships
class UserSerializer(serializers.ModelSerializer):
    groups = NestedUserGroupSerializer(source='usergroup_set', many=True, read_only=True)
    
    class Meta:
        model = models.User
        fields = '__all__'

class GroupSerializer(serializers.ModelSerializer):
    members = NestedGroupUserSerializer(source='usergroup_set', many=True, read_only=True)
    
    class Meta:
        model = models.Group
        fields = '__all__'

class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Goal
        fields = '__all__'

class SituationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Situation
        fields = '__all__'

class ObservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Observation
        fields = '__all__'

class StatusSerializer(serializers.ModelSerializer):
    goals = NestedStatusGoalSerializer(source='statusgoal_set', many=True, read_only=True)
    
    class Meta:
        model = models.Status
        fields = '__all__'