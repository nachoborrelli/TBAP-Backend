from django.contrib import admin
from organization.models import Organization, InvitationToBecameUserAdmin


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display=['user', 'name']


@admin.register(InvitationToBecameUserAdmin)
class InvitationToBecameUserAdminAdmin(admin.ModelAdmin):
    list_display=['organization', 'email', 'status']