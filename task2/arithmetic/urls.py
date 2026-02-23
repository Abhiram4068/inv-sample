from .views import RegisterView, LoginView, LogoutView
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

app_name='arithmetic'


urlpatterns=[
     path('auth/register/', RegisterView.as_view(), name='register'),
     path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name="token_refresh"),
    path('auth/logout/', LogoutView.as_view(), name="user-logout"),
]