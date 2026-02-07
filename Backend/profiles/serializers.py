from rest_framework import serializers
from .models import Gallery, Committee


class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ('id', 'image', 'date', 'description', 'created_at')


class CommitteeSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    
    def get_name(self, obj):
        # Try to find family member linked to this user
        if hasattr(obj.user, 'member') and obj.user.member:
            return obj.user.member.name
        return obj.user.get_full_name() or obj.user.username

    def get_age(self, obj):
        if hasattr(obj.user, 'member') and obj.user.member:
             return obj.user.member.age
        return None

    class Meta:
        model = Committee
        fields = ('id', 'user', 'name', 'pic', 'role', 'age', 'created_at')
