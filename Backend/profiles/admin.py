from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Gallery, Committee

@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'description', 'image', 'created_at')
    list_filter = ('date',)
    search_fields = ('description',)

@admin.register(Committee)
class CommitteeAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'pic', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('user__username', 'role')
