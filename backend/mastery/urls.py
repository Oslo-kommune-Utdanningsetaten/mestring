from django.urls import path, include
from rest_framework.routers import DefaultRouter
from mastery import views

router = DefaultRouter()
router.register(r'schools', views.SchoolViewSet, basename="school")
router.register(r'subjects', views.SubjectViewSet, basename="subject")
router.register(r'users', views.UserViewSet, basename="user")
router.register(r'roles', views.RoleViewSet, basename="role")
router.register(r'groups', views.GroupViewSet, basename="group")
router.register(r'goals', views.GoalViewSet, basename="goal")
router.register(r'situations', views.SituationViewSet, basename="situation")
router.register(r'observations', views.ObservationViewSet, basename="observation")
router.register(r'status', views.StatusViewSet, basename="status")
router.register(r'user-groups', views.UserGroupViewSet, basename="user-group")
router.register(r'status-goals', views.StatusGoalViewSet, basename="status-goal")

urlpatterns = [
    path('', include(router.urls)),
]
