from django.urls import path
from organization.views import SendAdminInvitation, AdminsOfOrganization

urlpatterns = [
    path('send-admin-invitation/', SendAdminInvitation.as_view(), name='send_admin_invitation'),
    path('admins-of-organization/', AdminsOfOrganization.as_view(), name='admins_of_organization'),
]