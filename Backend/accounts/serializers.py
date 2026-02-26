from rest_framework import serializers
from .models import User
from families.models import FamilyMember

class ManagedMemberSerializer(serializers.ModelSerializer):
    profile_pic = serializers.SerializerMethodField()

    class Meta:
        model = FamilyMember
        fields = ('id', 'name', 'profile_pic', 'relation')

    def get_profile_pic(self, obj):
        if obj.photo:
            return obj.photo.url
        return None

class UserSerializer(serializers.ModelSerializer):
    profile_pic = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    role = serializers.ReadOnlyField()
    managed_members = ManagedMemberSerializer(many=True, read_only=True)

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
            'managed_members',
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
