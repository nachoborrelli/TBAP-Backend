from django.urls import path

from user_admin.views import CourseView, ResponseInvitationToBecameUserAdminView, \
SendInvitationToJoinCourseAsUser, ResponseInvitationToJoinCourseAsAdminView, SendInvitationToJoinCourseAsAdmin


urlpatterns = [
    path('invitations-to-became-admin/', ResponseInvitationToBecameUserAdminView.as_view(), name='invitation'),
    path('course/', CourseView.as_view(), name='course'),
    path('send-invitation-to-join-course-as-admin/', SendInvitationToJoinCourseAsAdmin.as_view(), name='send-invitation-to-join-course-as-admin'),
    path('send-invitation-to-join-course-as-user/', SendInvitationToJoinCourseAsUser.as_view(), name='send-invitation-to-join-course-as-user'),
    path('response-invitation-to-join-course-as-admin/', ResponseInvitationToJoinCourseAsAdminView.as_view(), name='accept-invitation-to-join-course-as-admin'),
]