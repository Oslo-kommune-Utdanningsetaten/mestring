from mastery import models, serializers
from rest_framework import viewsets, status, views, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

# More about filtering in Django REST Framework:
# https://www.django-rest-framework.org/api-guide/filtering/

class SchoolViewSet(viewsets.ModelViewSet):
    queryset = models.School.objects.all()
    serializer_class = serializers.SchoolSerializer
    filterset_fields = ['is_service_enabled']

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = models.Subject.objects.all()
    serializer_class = serializers.SubjectSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    
    @action(detail=True, methods=['get'])
    def groups(self, request, pk=None):
        """Retrieve all groups a user belongs to"""
        user = self.get_object()
        user_groups = models.UserGroup.objects.filter(user=user)
        serializer = serializers.NestedUserGroupSerializer(user_groups, many=True)
        return Response(serializer.data)

class RoleViewSet(viewsets.ModelViewSet):
    queryset = models.Role.objects.all()
    serializer_class = serializers.RoleSerializer

class GroupViewSet(viewsets.ModelViewSet):
    queryset = models.Group.objects.all()
    serializer_class = serializers.GroupSerializer
    filterset_fields = ['school']
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Retrieve all members of a group"""
        group = self.get_object()
        group_members = models.UserGroup.objects.filter(group=group)
        serializer = serializers.NestedGroupUserSerializer(group_members, many=True)
        return Response(serializer.data)

class GoalViewSet(viewsets.ModelViewSet):
    queryset = models.Goal.objects.all()
    serializer_class = serializers.GoalSerializer

class SituationViewSet(viewsets.ModelViewSet):
    queryset = models.Situation.objects.all()
    serializer_class = serializers.SituationSerializer

class ObservationViewSet(viewsets.ModelViewSet):
    queryset = models.Observation.objects.all()
    serializer_class = serializers.ObservationSerializer

class StatusViewSet(viewsets.ModelViewSet):
    queryset = models.Status.objects.all()
    serializer_class = serializers.StatusSerializer

class UserGroupViewSet(viewsets.ModelViewSet):
    queryset = models.UserGroup.objects.all()
    serializer_class = serializers.UserGroupSerializer

