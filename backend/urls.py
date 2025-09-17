from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from mastery.api import auth, custom

urlpatterns = [
    path('api/', include('mastery.urls')),
    path('api/schema/', SpectacularAPIView.as_view(),
         name='schema'),
    path(
        'api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui'),
    path('api/ping/', custom.ping, name='ping'),
    path('auth/feidelogin/', auth.feidelogin, name='feide_login'),
    path('auth/feidecallback', auth.feidecallback, name='feide_callback'),
    path('auth/logout/', auth.feidelogout, name='feide-logout'),
    path('auth/status', auth.auth_status, name='auth_status'),
    path(
        'api/fetch/groups/feide/<str:org_number>/',
        custom.fetch_groups_for_school,
        name='fetch_groups_for_school'
    ),
    path(
        'api/fetch/memberships/feide/<str:org_number>/',
        custom.fetch_memberships_for_school,
        name='fetch_memberships_for_school'
    ),
    path(
        'api/import/school/feide/<str:org_number>/',
        custom.import_school,
        name='feide_import_school_api'
    ),
    path(
        'api/import/school_groups_and_users/<str:org_number>/',
        custom.import_groups_and_users,
        name='import_groups_and_users'
    ),
    path(
        'api/fetch/school_import_status/<str:org_number>/',
        custom.fetch_school_import_status,
        name='fetch_school_import_status'
    )
]
