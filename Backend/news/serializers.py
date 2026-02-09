from rest_framework import serializers
from .models import Post, Media

class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = '__all__'

class PostSerializer(serializers.ModelSerializer):
    # Include media if needed
    media = MediaSerializer(many=True, read_only=True)
    creator_name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    
    def get_creator_name(self, obj):
        if obj.creator:
            return obj.creator.name
        return "Unknown"
    
    def get_image(self, obj):
        # Return first image from media if exists
        first_media = obj.media.filter(media_type='image').first()
        if first_media and first_media.media_url:
            return first_media.media_url.url
        return None

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
            'media',
            'image'
        )
