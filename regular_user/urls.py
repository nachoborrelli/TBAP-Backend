from django.urls import path

from regular_user.views import InvitationToJoinCourseView, UserCoursesView


urlpatterns = [
    path('invitations-to-join-course-as-user/', InvitationToJoinCourseView.as_view(), name='invitation'),
    path('courses/', UserCoursesView.as_view(), name='courses'),


]