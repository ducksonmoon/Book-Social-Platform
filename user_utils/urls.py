from django.urls import path
from . import views


app_name = "main"   

urlpatterns = [
    path("password_reset", views.password_reset_request, name="password_reset"),
    path("password_reset_api/", views.PasswordResetAPI.as_view(), name="password_reset_api"),
    path("google_auth/", views.GoolgeAuth.as_view(), name="google_login"),
]