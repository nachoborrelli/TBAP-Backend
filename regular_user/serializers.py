from rest_framework import serializers
from regular_user.models import UserProfile, UserCourses
from user_admin.serializers import CourseSerializer


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ('user',)

class UserCoursesSerializer(serializers.ModelSerializer):
    course = CourseSerializer()
    class Meta:
        model = UserCourses
        fields = '__all__'
        read_only_fields = ('user', 'course')
