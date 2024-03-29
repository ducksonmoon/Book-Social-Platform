from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('verify-email/', views.VerifyEmailView.as_view(), name='verify-email'),
    path('send-email/', views.SendConfirmCodeView.as_view(), name='send-code'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('me/', views.ManageUserView.as_view(), name='me'),
    path('me/change_password/', views.ChangePasswordView.as_view(), name='change_password'),
    # 3 invitation code for user
    path('me/invitations/', views.InvitationView.as_view(), name='my_invitations'),
    # Enter invitation code
    path('me/invitation_code/enter/', views.InvitationCodeView.as_view(), name='invitation_code_enter'),
]
