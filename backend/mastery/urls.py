from django.urls import path, include
from rest_framework.routers import SimpleRouter
from mastery.api import views

router = SimpleRouter()
router.register(r'schools', views.SchoolViewSet, basename="school")
router.register(r'subjects', views.SubjectViewSet, basename="subject")
router.register(r'users', views.UserViewSet, basename="user")
router.register(r'user-schools', views.UserSchoolViewSet, basename="user-school")
router.register(r'user-groups', views.UserGroupViewSet, basename="user-group")
router.register(r'roles', views.RoleViewSet, basename="role")
router.register(r'groups', views.GroupViewSet, basename="group")
router.register(r'goals', views.GoalViewSet, basename="goal")
router.register(r'situations', views.SituationViewSet, basename="situation")
router.register(r'observations', views.ObservationViewSet, basename="observation")
router.register(r'status', views.StatusViewSet, basename="status")
router.register(r'mastery-schemas', views.MasterySchemaViewSet, basename="mastery-schema")
router.register(r'data-maintenance-tasks', views.DataMaintenanceTaskViewSet, basename="data-maintenance-task")

urlpatterns = [
    path('', include(router.urls)),
]
