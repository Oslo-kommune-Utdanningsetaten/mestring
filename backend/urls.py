from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from mastery.api import auth, custom

urlpatterns = [
    path('api/', include('mastery.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/ping/', custom.ping, name='ping'),
    path('auth/feidelogin/', auth.feidelogin, name='feide_login'),
    path('auth/feidecallback', auth.feidecallback, name='feide_callback'),
    path('auth/logout/', auth.feidelogout, name='feide-logout'),
    path('auth/status', auth.auth_status, name='auth_status'),
    path('api/import/school/feide/<str:org_number>/', custom.feide_import_school_api, name='feide-import-school-api'),
    path('api/fetch/groups/feide/<str:org_number>/', custom.feide_fetch_groups_for_school_api, name='feide-fetch-groups-school'),
    path('api/fetch/users/feide/<str:org_number>/', custom.feide_fetch_users_for_school_api, name='feide-fetch-users-school'),
    path('api/import/school_groups_and_users/<str:org_number>/', custom.import_groups_and_users_api, name='import-groups-and-users-api'),
]
