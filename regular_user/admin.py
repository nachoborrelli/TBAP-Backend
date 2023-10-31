from django.contrib import admin
from regular_user.models import UserProfile, UserCourses
from user_admin.models import InvitationToCourseAsUser

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display=['user', 'wallet_address']

@admin.register(UserCourses)
class UserCoursesAdmin(admin.ModelAdmin):
    list_display=['user', 'course']


@admin.register(InvitationToCourseAsUser)
class InvitationToCourseAsUserAdmin(admin.ModelAdmin):
    list_display=['email', 'course', 'status', 'created_at']
