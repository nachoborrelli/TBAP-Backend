from django.contrib import admin
from user_admin.models import Admin, Course, AdminCourses

@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    list_display=['user', 'organization']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display=['name', 'description']


@admin.register(AdminCourses)
class AdminCoursesAdmin(admin.ModelAdmin):
    list_display=['user', 'admin', 'course']

    def user(self, obj):
        return obj.admin.user

    user.short_description = 'User'