from .views import RegisterView, LoginView, LogoutView, AddView, SubtractView, MultiplyView, DivideView
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

app_name='arithmetic'


urlpatterns=[
     path('auth/register/', RegisterView.as_view(), name='register'),
     path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name="token_refresh"),
    path('auth/logout/', LogoutView.as_view(), name="user-logout"),
    
    path('calculate/add/<int:num1>/<int:num2>/', AddView.as_view(), name='calaculate-add'),
    path('calculate/subtract/<int:num1>/<int:num2>/', SubtractView.as_view(), name='calaculate-subtract'),
    path('calculate/multiply/<int:num1>/<int:num2>/', MultiplyView.as_view(), name='calaculate-multiply'),
    path('calculate/divide/<int:num1>/<int:num2>/', DivideView.as_view(), name='calaculate-divide'),
]