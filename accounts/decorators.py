from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

def role_required(*roles, verified=False):
    def decorator(view):
        @login_required
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            profile = getattr(request.user, "profile", None)
            if profile is None or profile.role not in roles:
                raise PermissionDenied
            if verified and not profile.is_verified:
                raise PermissionDenied
            return view(request, *args, **kwargs)
        return wrapper
    return decorator