from django.urls import path

from users.register_views import PasswordRecoveryEmailSend, CheckToken, PasswordRecoveryConfirm,PasswordChangeViewModify
from users.views import UserProfileMe, LoginView, RecepcionOauthView


urlpatterns = [
    # Account management
    path('password-change/', PasswordChangeViewModify.as_view(), name='rest_password_change'),
    path('password-recovery/', PasswordRecoveryEmailSend.as_view(), name='password_recovery_email_send'),
    path('password-recovery/check-token/', CheckToken.as_view(), name='check_token'),
    path('password-recovery/confirm/', PasswordRecoveryConfirm.as_view(), name='password_recovery_confirm'),

    # User management
    path('me/', UserProfileMe.as_view(), name='user_profile_me'),
    path('login/', LoginView.as_view(), name='login'),
    path('oauth/', RecepcionOauthView.as_view(), name='oauth'),

]