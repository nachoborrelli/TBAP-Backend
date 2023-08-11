from django.contrib import admin

# Register your models here.

from .models import TokenGroup, UserToken, Signature

@admin.register(TokenGroup)
class TokenGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'created_at', 'created_by')
    search_fields = ('name', 'course__name', 'created_by__email')
    list_filter = ('course', 'created_at', 'created_by')

@admin.register(UserToken)
class UserTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token_group', 'created_at', 'is_claimed')
    search_fields = ('user__email', 'token_group__name')
    list_filter = ('token_group', 'created_at', 'is_claimed')

@admin.register(Signature)
class SignatureAdmin(admin.ModelAdmin):
    list_display = ('user', 'token_name', 'organization', 'uri', 'nonce')
    search_fields = ('user__email', 'token_name', 'organization__name', 'uri')
    list_filter = ('organization', 'user')
    