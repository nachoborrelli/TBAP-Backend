from django.contrib import admin
from regular_user.models import UserProfile, UserCourses

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display=['user', 'wallet_address']

@admin.register(UserCourses)
class UserCoursesAdmin(admin.ModelAdmin):
    list_display=['user', 'course']
