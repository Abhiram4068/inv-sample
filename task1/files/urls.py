from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from files.views import RegisterView, LoginView, LogoutView, FileCreateView, FileReadView, FileDetailReadView, FileUpdateView, FileDeleteView

app_name='files'

urlpatterns=[
    
    path('auth/register/', RegisterView.as_view(), name='user-register'),
    path('auth/login/', LoginView.as_view(), name='user-login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name="token_refresh"),
    path('auth/logout/', LogoutView.as_view(), name="user-logout"),

    path('files/create/', FileCreateView.as_view(), name='file-create'),
    path('files/read/', FileReadView.as_view(), name='file-read'),
    path('files/<uuid:pk>/read/', FileDetailReadView.as_view(), name='file-detail'),
    path('files/<uuid:pk>/update/', FileUpdateView.as_view(), name='file-update'),
    path('files/<uuid:pk>/delete/', FileDeleteView.as_view(), name='file-delete'),
]