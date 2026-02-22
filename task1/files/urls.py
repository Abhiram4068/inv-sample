from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from files.views import RegisterView, LoginView, LogoutView

app_name='files'

urlpatterns=[
    
    path('auth/register/', RegisterView.as_view(), name='user-register'),
    path('auth/login/', LoginView.as_view(), name='user-login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name="token_refresh"),
    path('auth/logout/', LogoutView.as_view(), name="user-logout"),
]