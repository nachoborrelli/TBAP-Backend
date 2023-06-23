from rest_framework import serializers
from user_admin.models import Admin, Course, AdminCourses

class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = ('user', 'organization')
        read_only_fields = ('user',)

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ('name', 'description')

class AdminCoursesSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminCourses
        fields = ('admin', 'course')

