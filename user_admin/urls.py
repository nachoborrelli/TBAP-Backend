from django.urls import path

from user_admin.views import CourseView


urlpatterns = [
    path('course/', CourseView.as_view(), name='course'),

]