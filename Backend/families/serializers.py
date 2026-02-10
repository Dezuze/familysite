from rest_framework import serializers
from .models import FamilyMember

class FamilyMemberSerializer(serializers.ModelSerializer):
    role = serializers.ReadOnlyField()
    profile_pic = serializers.SerializerMethodField()

    class Meta:
        model = FamilyMember
        fields = '__all__'

    def get_profile_pic(self, obj):
        if obj.photo:
            return obj.photo.url
        return None

class FamilyTreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyMember
        fields = ['id', 'name', 'parents', 'children']
        depth = 1 # Simple depth to see Names of related objects

from .models import FamilyMedia
class FamilyMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyMedia
        fields = '__all__'
