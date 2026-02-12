from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.admin.sites import NotRegistered
from unfold.admin import ModelAdmin
from .models import User, InviteToken

# Unregister any existing registration for the User model (prevents duplicate links)
try:
    admin.site.unregister(User)
except NotRegistered:
    pass

@admin.register(User)
class UserAdmin(auth_admin.UserAdmin, ModelAdmin):
    list_display = (
        'username',
        'email',
        'member',
        'is_active',
        'is_staff'
    )
    search_fields = ('username', 'email')
    list_filter = ('is_active', 'is_staff')
    ordering = ('username',)

@admin.register(InviteToken)
class InviteTokenAdmin(ModelAdmin):
    list_display = ('token', 'member', 'is_used', 'created_at')
    list_filter = ('is_used', 'created_at')
    readonly_fields = ('token', 'created_at')
