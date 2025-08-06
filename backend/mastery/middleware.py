import re
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from mastery.models import User

class CamelCaseQueryParamMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Convert camelCase query params to snake_case
        if request.GET:
            new_params = request.GET.copy()
            for key in list(request.GET.keys()):
                snake_case_key = re.sub(r'([A-Z])', r'_\1', key).lower()
                if snake_case_key != key:  # Only if conversion happened
                    new_params[snake_case_key] = request.GET[key]
            request.GET = new_params
        return None


class UpdateUserActivityMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Update user's last activity timestamp if user is authenticated
        if hasattr(request, 'session') and "feide_user_id" in request.session:
            user_id = request.session["feide_user_id"]
            try:
                User.objects.filter(id=user_id).update(
                    last_activity_at=timezone.now()
                )
            except Exception:
                pass
        return None
