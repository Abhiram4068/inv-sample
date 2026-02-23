from django.db import transaction, IntegrityError
from django.contrib.auth import get_user_model
User = get_user_model()
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from typing import List
from .models import File
import hashlib
from rest_framework.exceptions import NotFound, PermissionDenied
from django.utils import timezone
from django.core.files.storage import default_storage
from django.http import FileResponse
from django.shortcuts import get_object_or_404

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

    @staticmethod
    def read_files(user):
        all_files=File.objects.filter(user=user, is_deleted=False)
        return all_files
    
    @staticmethod
    def read_file_details(user, pk):
        try:
            
            file_details=File.objects.get(user=user, id=pk, is_deleted=False)
        except File.DoesNotExist:
            raise NotFound("File not found.")
        return file_details
    
    @staticmethod
    @transaction.atomic
    def update_file(user, file_id, validated_data):
        try:
            file_instance = File.objects.get(
                id=file_id,
                user=user,
                is_deleted=False
            )
        except File.DoesNotExist:
            raise NotFound("File not found.")

        new_file = validated_data.get("file")
        description = validated_data.get("description")

        if new_file:
            checksum = FileService._calculate_checksum(new_file)

            existing_file = File.objects.filter(
                checksum=checksum,
                is_deleted=False
            ).first()


            if file_instance.file:
                default_storage.delete(file_instance.file.name)

            if existing_file:
                file_instance.file = existing_file.file
            else:
                file_instance.file = new_file

            file_instance.original_name = new_file.name
            file_instance.file_size = new_file.size
            file_instance.content_type = new_file.content_type
            file_instance.checksum = checksum

        if description is not None:
            file_instance.description = description

        file_instance.updated_at = timezone.now()
        file_instance.save()

        return file_instance
    
    @staticmethod
    def delete_file(user, file_id):
        try:
            file_instance=File.objects.get(user=user, id=file_id, is_deleted=False)
        except File.DoesNotExist:
            raise NotFound("File not found.")
        checksum = file_instance.checksum
        file_instance.is_deleted=True
        file_instance.deleted_at=timezone.now()
        file_instance.save(update_fields=['is_deleted', 'deleted_at'])

        return {
            "id": str(file_instance.id),
            "message": "File deleted successfully"
        }
    
    @staticmethod
    def download_file(user, file_id):
        file_obj=get_object_or_404(File, id=file_id, user=user)

        return FileResponse(
            file_obj.file.open('rb'),
            as_attachment=False,
            filename=file_obj.original_name
        )
class FileStorageService:
    @classmethod
    def get_valid_file(cls, file_id, user):
        return get_object_or_404(
            File, 
            id=file_id, 
            user=user
        )