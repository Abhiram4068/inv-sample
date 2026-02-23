from rest_framework import serializers
from django.contrib.auth import get_user_model
User=get_user_model()
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.db import models
from .models import File

class RegisterSerialzier(serializers.ModelSerializer):
    confirm_password=serializers.CharField(write_only=True, min_length=8)
    class Meta:
        model=User
        fields=[
            'username',
            'password',
            'confirm_password',
            'first_name',
            'last_name'
        ]
        extra_kwargs={
            'password':{'write_only':True, 'min_length':8},
            'last_name':{'required':False},
        }
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                {'username':'Username already exists!'}
            )
        return value
    def validate(self, attrs):
        password=attrs.get('password')
        confirm_password=attrs.get('confirm_password')
        if password!=confirm_password:
            raise serializers.ValidationError(
                {'confirm_password':'Passwords doesnt match'}
            )
        validate_password(password)
        attrs.pop('confirm_password')
        return attrs
    
class LoginSerializer(serializers.Serializer):
    username=serializers.CharField(required=True)
    password=serializers.CharField(required=True, write_only=True)
    
class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()



class FileCreateSerializer(serializers.Serializer):
    files = serializers.ListField(
        child=serializers.FileField(
            max_length=100000000,
            allow_empty_file=False
        ),
        allow_empty=False
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )

    def validate(self, data):
        max_file_size = 10 * 1024 * 1024

        for file in data.get('files', []):
            if file.size > max_file_size:
                raise serializers.ValidationError(
                    f"File '{file.name}' exceeds maximum size of 10MB."
                )
        return data


class FileReadSerializer(serializers.ModelSerializer):
    class Meta:
        model=File
        fields=[
            'user',
            'id',
            'file',
            'original_name',
            'file_size',
            'content_type',
            'created_at'
        ]
    