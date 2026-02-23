from django.db import transaction, IntegrityError
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed, ValidationError

class UserAuthService:
    @staticmethod
    def user_register(validated_data):
        email=validated_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValueError('Email already exists!')
        try:
            with transaction.atomic():
                return User.objects.create_user(**validated_data)
        except IntegrityError:
            raise ValueError('Cant complete user registrartion right now. Please try again later!')
        
    @staticmethod
    def user_login(email:str, password:str):
        try:
            user=User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValueError("User not found")
        if not user.check_password(password):
            raise ValueError("Invalid credentials")
        if not user.is_active:
            raise ValueError("Account is disabled")
        refresh=RefreshToken.for_user(user)
        return {
            'user':user,
            'tokens':{
                'access':str(refresh.access_token),
                'refresh':str(refresh)
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