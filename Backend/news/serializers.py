from rest_framework import serializers
from .models import Post, Media


class MediaSerializer(serializers.ModelSerializer):
    media_url = serializers.SerializerMethodField()

    def get_media_url(self, obj):
        if obj.media_url:
            return obj.media_url.url
        return None

    class Meta:
        model = Media
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    # Include media if needed
    media = MediaSerializer(many=True, read_only=True)
    creator_name = serializers.SerializerMethodField()
    author_id = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    celebration_type = serializers.SerializerMethodField()

    def get_creator_name(self, obj):
        if obj.creator:
            return obj.creator.name
        return "Unknown"

    def get_author_id(self, obj):
        if obj.creator and hasattr(obj.creator, 'user_account'):
            return obj.creator.user_account.id
        return None

    def get_image(self, obj):
        # Return first image from media if exists
        first_media = obj.media.filter(media_type='image').first()
        if first_media and first_media.media_url:
            return first_media.media_url.url
        return None

    def get_celebration_type(self, obj):
        if not obj.is_auto_generated:
            return None
        first_media = obj.media.filter(media_type='image').first()
        if first_media and first_media.media_url:
            name = first_media.media_url.name or ''
            if 'birthday_' in name:
                return 'birthday'
            if 'wedding_anniversary_' in name:
                return 'wedding_anniversary'
            if 'death_anniversary_' in name:
                return 'death_anniversary'
        title_lower = (obj.title or '').lower()
        if 'birthday' in title_lower:
            return 'birthday'
        if 'wedding anniversary' in title_lower or 'anniversary' in title_lower:
            return 'wedding_anniversary'
        if 'remembering' in title_lower or 'memory' in title_lower:
            return 'death_anniversary'
        return 'celebration'

    class Meta:
        model = Post
        fields = (
            'id',
            'title',
            'description',
            'post_type',
            'event_date',
            'location',
            'created_at',
            'creator_name',
            'author_id',
            'media',
            'image',
            'is_kudumbayogam',
            'is_auto_generated',
            'celebration_type',
        )
