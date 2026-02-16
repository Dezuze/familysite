from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Post, Media

@admin.register(Post)
class PostAdmin(ModelAdmin):
    list_display = ('title', 'post_type', 'location', 'created_at')
    list_filter = ('post_type', 'created_at')
    search_fields = ('title',)
    ordering = ('-created_at',)

@admin.register(Media)
class MediaAdmin(ModelAdmin):
    list_display = ('id', 'uploader', 'post', 'media_type', 'uploaded_at')
    list_filter = ('media_type', 'uploaded_at', 'post')
    search_fields = ('media_type', 'caption')
    readonly_fields = ('uploaded_at',)
