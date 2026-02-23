from rest_framework import serializers
from .models import User
from django.contrib.auth.password_validation import validate_password


class RegisterSerializer(serializers.ModelSerializer):
    confirm_password=serializers.CharField(min_length=8, write_only=True)
    class Meta:
        model=User
        fields=[
            'email',
            'password',
            'first_name',
            'last_name',
            'confirm_password'
        ]
        extra_kwargs={
            'password':{'write_only':True, 'min_length':8},
            'last_name':{'required':False}
        }
        
    def validate_email(self, value):
        return value.lower().strip()
    def validate(self, attrs):
        password=attrs['password']
        confirm_password=attrs['confirm_password']
        if password!=confirm_password:
            raise serializers.ValidationError({'password':'Passwords doesnt match'})
        validate_password(password)
        attrs.pop('confirm_password')
        return attrs
    
class LoginSerializer(serializers.Serializer):
    email=serializers.EmailField(required=True)
    password=serializers.CharField(
        write_only=True,
        required=True
    )
class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()