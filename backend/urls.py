from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from mastery.views import ping
from mastery import auth 

urlpatterns = [
    path('api/', include('mastery.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/ping/', ping, name='ping'),
    path('auth/feidelogin/', auth.feidelogin, name='feide_login'),
    path('auth/feidecallback', auth.feidecallback, name='feide_callback'),
    path('auth/logout/', auth.feidelogout, name='feide-logout'),
    path('api/auth/status', auth.auth_status, name='auth_status'),
]
