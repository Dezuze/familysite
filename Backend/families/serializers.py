from rest_framework import serializers
from .models import FamilyMember

class FamilyMemberSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField()
    age = serializers.ReadOnlyField()
    role = serializers.ReadOnlyField()
    
    class Meta:
        model = FamilyMember
        fields = '__all__'

class FamilyTreeSerializer(serializers.ModelSerializer):
    # Simplified structure for D3
    class Meta:
        model = FamilyMember
        fields = ['id', 'name', 'parents', 'spouse', 'children']
        depth = 1 # Simple depth to see Names of related objects
