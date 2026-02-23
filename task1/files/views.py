from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .services import UserAuthService, FileService
from .serializers import RegisterSerialzier, LoginSerializer, LogoutSerializer, FileCreateSerializer, FileReadSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status

class RegisterView(APIView):
    authentication_classes=[]
    permission_classes=[AllowAny]
    
    def post(self, request):
        serializer=RegisterSerialzier(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user=UserAuthService.user_register(serializer.validated_data)
            return Response(
                {
                    'message':'User registered successfully',
                    'user_id':user.id
                },
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response(
                {'error':str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
class LoginView(APIView):
    permission_classes=[AllowAny]
    authentication_classes=[]
    
    def post(self, request):
        serializer=LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            result=UserAuthService.user_login(serializer.validated_data['username'], serializer.validated_data['password'])
        except ValueError as e:
            return Response(
                {'error':str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        user=result['user']
        tokens=result['tokens']
        return Response(
            {'message':'Login successfull',
             'user':{
                 'id':user.id,
                 'first_name':user.first_name
             },
             'tokens':tokens
             },
            
            status=status.HTTP_200_OK
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
        
            
class FileCreateView(APIView):
    permission_classes=[IsAuthenticated]
    
    def post(self, request):
        serializer=FileCreateSerializer(
            data=request.data,
            context={'request':request}
            )
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        files=serializer.validated_data['files']
        description = serializer.validated_data.get("description")
        try:
            uploaded_files=FileService.create_files(user=request.user, files=files, description=description) 
            return Response(
                {
                    'message':f'{len(uploaded_files)} files uploaded successfully',
                    'files':uploaded_files
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error':str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )       
         
class FileReadView(APIView):
    permission_class=[IsAuthenticated]
    def get(self, request):
        all_files=FileService.read_files(request.user)
        if not all_files.exists():
            return Response(
                {'message':'You haven"t uploaded any files yet.'},
                status=status.HTTP_200_OK
            )
        serializer=FileReadSerializer(all_files, many=True)
        return Response(serializer.data)
    
class FileDetailReadView(APIView):
    permission_classes=[IsAuthenticated]

    def get(self, request, pk):
        file_details=FileService.read_file_details(request.user, pk)
        if not file_details:
            return Response(
                {'message':'File not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer=FileReadSerializer(file_details)
        return Response(serializer.data)
