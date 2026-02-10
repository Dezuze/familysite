from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    profile_pic = serializers.SerializerMethodField()
    role = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'member',
            'role',
            'profile_pic'
        )

    def get_profile_pic(self, obj):
        if obj.member and obj.member.photo:
            return obj.member.photo.url
        return None
