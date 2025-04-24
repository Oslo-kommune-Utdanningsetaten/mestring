from mastery import models, serializers
from rest_framework import viewsets, status, views, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response


class SchoolViewSet(viewsets.ModelViewSet):
    queryset = models.School.objects.all()
    serializer_class = serializers.SchoolSerializer
