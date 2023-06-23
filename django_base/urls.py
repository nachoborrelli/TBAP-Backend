from django.contrib import admin
from django.urls import path, re_path
from django.conf.urls import include
from users.register_views import EmailVerification
from dj_rest_auth.registration.views import ResendEmailVerificationView, RegisterView
from dj_rest_auth.views import LoginView, LogoutView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth
    path('login/', LoginView.as_view(),name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/', RegisterView.as_view(), name='signup'),
    re_path("signup/account-confirm-email/(?P<key>[\s\d\w().+-_',:&]+)/$", EmailVerification.as_view(), name='account_confirm_email'),
    path('account-email-verification-sent/', EmailVerification.as_view(), name='account_email_verification_sent'),
    path('resend-email/', ResendEmailVerificationView.as_view(), name="rest_resend_email"),

    # Apps
    path('api/users/', include('users.urls')),
    path('api/blockchain/', include('blockchain.urls')),
    path('api/organization/', include('organization.urls')),
    path('api/admin/', include('user_admin.urls')),
    # path('api/regular_user/', include('regular_user.urls')),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
