from django.urls import path
from organization.views import SendAdminInvitation, AdminsOfOrganization, OrganizationView, \
                                InvitationsSentView

urlpatterns = [
    path("", OrganizationView.as_view(), name="create_organization"),
    path('send-admin-invitation/', SendAdminInvitation.as_view(), name='send_admin_invitation'),
    path('invitations-sent/', InvitationsSentView.as_view(), name='invitations_sent'),
    path('admins/', AdminsOfOrganization.as_view(), name='admins_of_organization'),
]
