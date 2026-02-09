from django.contrib import admin
from .models import Post, Media

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'post_type', 'location', 'created_at')
    list_filter = ('post_type', 'created_at')
    search_fields = ('title',)
    ordering = ('-created_at',)

@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('id', 'media_type', 'uploaded_at')
