import re
from django.utils.deprecation import MiddlewareMixin

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
