from django.db import transaction, IntegrityError
from django.contrib.auth import get_user_model
User = get_user_model()
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from typing import List
from .models import File
import hashlib

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
    

class FileService:

    @staticmethod
    def _calculate_checksum(file_obj):
        hash_md5 = hashlib.md5()
        file_obj.seek(0)
        for chunk in file_obj.chunks():
            hash_md5.update(chunk)
        file_obj.seek(0)
        return hash_md5.hexdigest()

    @staticmethod
    @transaction.atomic
    def create_files(user, files:List, description=None):
        uploaded_files=[]
        for file_obj in files:
            checksum=FileService._calculate_checksum(file_obj)
            existing_file=File.objects.filter(checksum=checksum).first()
            if existing_file:
                file_instance=File.objects.create(
                    user=user,
                    file=existing_file.file,
                    original_name=file_obj.name,
                    description=description,
                    file_size=file_obj.size,
                    content_type=file_obj.content_type,
                    checksum=checksum
                )
                is_duplicate=True
            else:
                file_instance=File.objects.create(
                    user=user,
                    file=file_obj,
                    original_name=file_obj.name,
                    description=description,
                    file_size=file_obj.size,
                    content_type=file_obj.content_type,
                    checksum=checksum
                )
                is_duplicate=False
            uploaded_files.append({
                'id':str(file_instance.id),
                'name':file_instance.original_name,
                "size": file_instance.file_size,
                "content_type": file_instance.content_type,
                "checksum": file_instance.checksum,
                "created_at": file_instance.created_at,
                "is_duplicate": is_duplicate,
            })
        return uploaded_files

