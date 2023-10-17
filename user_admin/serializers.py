from rest_framework import serializers
from user_admin.models import Admin, Course, AdminCourses, InvitationToCourseAsUser
from users.serializers import UserSerializer

class AdminSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Admin
        fields = '__all__'
        read_only_fields = ('user',)

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'


class AdminCoursesSerializer(serializers.ModelSerializer):
    admin = AdminSerializer()
    course = CourseSerializer()
    class Meta:
        model = AdminCourses
        fields = ('admin', 'course')

class CoursesForAdminSerializer(serializers.ModelSerializer):   
    admins_in_course = serializers.SerializerMethodField()
    class Meta:
        model = Course
        fields = '__all__'

    def get_admins_in_course(self, obj):
        admin_ids = AdminCourses.objects.filter(course=obj).values('admin')
        admins = Admin.objects.filter(id__in=admin_ids)
        admins_data = AdminSerializer(admins, many=True).data
        return admins_data
        

class InvitationToCourseAsUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvitationToCourseAsUser
        fields = '__all__'
        read_only_fields = ('status', 'created_at')