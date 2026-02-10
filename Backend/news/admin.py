from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Post, Media

@admin.register(Post)
class PostAdmin(ModelAdmin):
    list_display = ('title', 'post_type', 'location', 'created_at')
    list_filter = ('post_type', 'created_at')
    search_fields = ('title',)
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Article Content', {
            'fields': ('title', 'content', 'post_type')
        }),
        ('Metadata', {
            'fields': (('location', 'date'),)
        }),
    )

@admin.register(Media)
class MediaAdmin(ModelAdmin):
    list_display = ('id', 'media_type', 'uploaded_at')
    list_filter = ('media_type', 'uploaded_at')
    search_fields = ('media_type',)
