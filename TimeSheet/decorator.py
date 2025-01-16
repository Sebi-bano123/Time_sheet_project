#  Role-Based Authorization Decorator


from functools import wraps
from django.http import JsonResponse
from .models import UserRole
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model



def role_required(required_roles):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            try:
                user_role = UserRole.objects.get(user=request.user).role.name
                if user_role not in required_roles:
                    return JsonResponse({'error': 'Permission denied'}, status=403)
                return func(request, *args, **kwargs)
            except UserRole.DoesNotExist:
                return JsonResponse({'error': 'User role not assigned'}, status=403)
        return wrapper
    return decorator



def login_required(view_func):
    """
    Decorator to ensure the user is authenticated via a JWT token.
    Returns a JSON error response if authentication fails.
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Retrieve the token from the Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Authentication credentials were not provided.'}, status=401)

        token = auth_header.split(' ')[1]  # Extract the token from "Bearer <token>"

        try:
            # Decode the JWT token
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_token.get('user_id')

            # Retrieve the user object
            user = get_user_model().objects.get(id=user_id)

            # Attach the authenticated user to the request
            request.user = user

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token has expired. Please log in again.'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Invalid token. Please log in again.'}, status=401)
        except get_user_model().DoesNotExist:
            return JsonResponse({'error': 'User not found. Invalid token.'}, status=401)
        except Exception as e:
            return JsonResponse({'error': f'Authentication failed: {str(e)}'}, status=401)

        # Proceed to the view if authentication succeeds
        return view_func(request, *args, **kwargs)

    return _wrapped_view
