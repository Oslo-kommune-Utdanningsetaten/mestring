from typing import Optional, Tuple
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from mastery.models import User


class SessionUserIdAuthentication(BaseAuthentication):
    """
    Authenticates using a 'user_id' stored in the session (set by Feide callback).
    Returns mastery.models.User as request.user.
    """

    def authenticate(self, request) -> Optional[Tuple[User, None]]:
        user_id = request.session.get("user_id")
        if not user_id:
            # AnonymousUser allowed for public endpoints, trust DRF to handle security
            return None, None
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed("Invalid session user")

        return user, None
