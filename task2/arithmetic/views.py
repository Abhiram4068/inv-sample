from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import RegisterSerializer, LoginSerializer, LogoutSerializer
from .services import UserAuthService, ArithmeticService
from rest_framework.response import Response
from rest_framework import status

class RegisterView(APIView):
    def post(self, request):
        serializer=RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user=UserAuthService.user_register(serializer.validated_data)
        except ValueError as e:
            return Response(
                {'error':str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )  
        return Response(
            {'message':'User registered successfully!',
             'user':user.id,
             'email':user.email
             },
            status=status.HTTP_201_CREATED
        )
        
class LoginView(APIView):
    authentication_classes=[]
    permission_classes=[AllowAny]
    
    def post(self, request):
        serializer=LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            result=UserAuthService.user_login(
                email=serializer._validated_data['email'],
                password=serializer.validated_data['password']
            )
        except ValueError as e:
            return Response(
                {'error':str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        user=result['user']
        tokens=result['tokens']
        return Response({
            'message':'Login successful',
            'user':{
                'id':user.id,
                'email':user.email,
                'first_name':user.first_name
                },
            'tokens':tokens
        },status=status.HTTP_200_OK
        )
        
        
class LogoutView(APIView):
    permission_classes=[IsAuthenticated]
    
    def post(self, request):
        serializer=LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token=serializer.validated_data['refresh_token']
        UserAuthService.user_logout(refresh_token)
        return Response(
            {'message':'Logout successful'},
            status=status.HTTP_205_RESET_CONTENT
        )
        
class AddView(APIView):
    permission_classes=[IsAuthenticated]
    
    def get(self, request, num1, num2):
        print(num1, num2)
        result=ArithmeticService.add(num1, num2)
        return Response({'Result':result}, status=status.HTTP_200_OK)
class SubtractView(APIView):
    permission_classes=[IsAuthenticated]
    
    def get(self, request, num1, num2):
        result=ArithmeticService.subtract(num1, num2)
        return Response({'Result':result}, status=status.HTTP_200_OK)
class MultiplyView(APIView):
    permission_classes=[IsAuthenticated]
    
    def get(self, request, num1, num2):
        result=ArithmeticService.multiply(num1, num2)
        return Response({'Result':result}, status=status.HTTP_200_OK)
class DivideView(APIView):
    permission_classes=[IsAuthenticated]
    
    def get(self, request,num1, num2):
        result=ArithmeticService.divide(num1, num2)
        return Response({'Result':result}, status=status.HTTP_200_OK)