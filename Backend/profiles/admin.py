from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Gallery, Committee

@admin.register(Gallery)
class GalleryAdmin(ModelAdmin):
    list_display = ('id', 'date', 'description', 'created_at')
    list_filter = ('date',)
    search_fields = ('description',)

@admin.register(Committee)
class CommitteeAdmin(ModelAdmin):
    list_display = ('user', 'role', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('user__username', 'role')
