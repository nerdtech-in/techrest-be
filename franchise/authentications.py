from rest_framework.permissions import BasePermission
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
import jwt
from django.conf import settings
from .models import Customer

class IsJWTAuthenticated(BaseAuthentication):
    def authenticate(self, request):
        try:
            token = request.headers.get('Authorization').split()[1]
        except:
            raise AuthenticationFailed("Token is missing")
        
        if not token:
            return None

        try:
            decoded_data = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')

        user_id = decoded_data.get('id')
        mobile_number = decoded_data.get('mobile_number')
        if user_id is None:
            return None
        
        try:
            customer = Customer.objects.get(mobile_number=mobile_number)
        except Customer.DoesNotExist:
            return None

        # Return the authenticated user and the token (None in this case)
        return customer, None