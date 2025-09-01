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
router.register(r'mastery-schemas', views.MasterySchemaViewSet, basename="mastery-schema")

urlpatterns = [
    path('', include(router.urls)),
    path('import/school/feide/<str:org_number>/', views.feide_import_school_api, name='feide-import-school-api'),
    path('fetch/groups/feide/<str:org_number>/', views.feide_fetch_groups_for_school_api, name='feide-fetch-groups-school'),
    path('fetch/users/feide/<str:org_number>/', views.feide_fetch_users_for_school_api, name='feide-fetch-users-school'),
    path('import/school_groups_and_users/<str:org_number>/', views.import_groups_and_users_api, name='import-groups-and-users-api'),
]
