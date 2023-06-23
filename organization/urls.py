from organization.views import SendAdminInvitation
from django.urls import path

urlpatterns = [
    path('send-admin-invitation/', SendAdminInvitation.as_view(), name='send_admin_invitation'),
]
