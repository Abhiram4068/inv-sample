from django.db import transaction, IntegrityError
from django.contrib.auth import get_user_model
User = get_user_model()
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed, ValidationError

class UserAuthService:
    @staticmethod
    def user_register(validated_data):
        try:
           with transaction.atomic():
               return User.objects.create_user(**validated_data)
        except IntegrityError:
            raise ValueError("Unable to create user right now please try again later")
        
    @staticmethod
    def user_login(username:str, password:str):
        try:
            user=User.objects.get(username=username)
        except User.DoesNotExist:
            raise AuthenticationFailed("Invalid credentials")
        if not user.check_password(password):
            raise AuthenticationFailed("Invalid credentials")
        if not user.is_active:
            raise ValueError("User not active")
        refresh_token=RefreshToken.for_user(user)
        return {
        'user':user,
        'tokens':{
            'access':str(refresh_token.access_token),
            'refresh':str(refresh_token)
        }
    }
        
    @staticmethod
    def user_logout(refresh_token : str):
        try:
            token=RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            raise AuthenticationFailed("Invalid or expired refresh token")
        return True