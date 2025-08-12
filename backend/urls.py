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
]
