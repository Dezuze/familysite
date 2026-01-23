from rest_framework import serializers
from .models import Post, Media

class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = '__all__'

class PostSerializer(serializers.ModelSerializer):
    # Include media if needed
    media = MediaSerializer(many=True, read_only=True)
    creator_name = serializers.CharField(source='creator.name', read_only=True)
    image = serializers.SerializerMethodField()
    
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
            'created_at',
            'creator_name',
            'media',
            'image'
        )
