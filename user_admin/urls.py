from django.urls import path

from user_admin.views import CourseView, ResponseInvitationToBecameUserAdminView, \
SendInvitationToJoinCourseAsUser, AddAdminToCourse, UsersInCourseView


urlpatterns = [
    path('invitations-to-became-admin/', ResponseInvitationToBecameUserAdminView.as_view(), name='invitation'),
    path('courses/', CourseView.as_view(), name='course'),
    path('add-admin-to-course/', AddAdminToCourse.as_view(), name='add-admin-to-course'),
    path('send-invitation-to-join-course-as-user/', SendInvitationToJoinCourseAsUser.as_view(), name='send-invitation-to-join-course-as-user'),
    path('users-in-course/', UsersInCourseView.as_view(), name='users-in-course'),
]