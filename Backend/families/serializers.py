from rest_framework import serializers
from .models import FamilyMember

class FamilyMemberSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    role = serializers.ReadOnlyField()

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name or ''}".strip()
    
    class Meta:
        model = FamilyMember
        fields = '__all__'

class FamilyTreeSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    
    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name or ''}".strip()

    class Meta:
        model = FamilyMember
        fields = ['id', 'name', 'parent', 'spouse', 'children']
        depth = 1 # Simple depth to see Names of related objects

from .models import FamilyMedia
class FamilyMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyMedia
        fields = '__all__'
