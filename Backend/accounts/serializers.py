from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    profile_pic = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    role = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'name',
            'member',
            'role',
            'profile_pic',
            'is_superuser',
            'is_staff'
        )

    def get_name(self, obj):
        if obj.member:
            return obj.member.name
        return obj.get_full_name()

    def get_profile_pic(self, obj):
        if obj.member and obj.member.photo:
            return obj.member.photo.url
        return None
