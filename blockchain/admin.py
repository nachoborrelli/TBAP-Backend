from django.contrib import admin

# Register your models here.

from .models import TokenGroup, UserToken, NonceTracker

@admin.register(TokenGroup)
class TokenGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'created_at', 'created_by')
    search_fields = ('name', 'course__name', 'created_by__email')
    list_filter = ('course', 'created_at', 'created_by')

@admin.register(UserToken)
class UserTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at', 'is_claimed')
    search_fields = ('user__email', 'token__name')
    list_filter = ('token', 'created_at', 'is_claimed')

@admin.register(NonceTracker)
class NonceTrackerAdmin(admin.ModelAdmin):
    list_display = ('nonce', 'created_at')
    search_fields = ('nonce',)
    list_filter = ('created_at',)