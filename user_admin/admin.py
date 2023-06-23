from django.contrib import admin
from user_admin.models import Admin, Course

@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    list_display=['user', 'organization']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display=['name', 'description']