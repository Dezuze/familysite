from rest_framework import serializers
from .models import FamilyMember

class FamilyMemberSerializer(serializers.ModelSerializer):
    role = serializers.ReadOnlyField()
    is_committee = serializers.ReadOnlyField()
    profile_pic = serializers.SerializerMethodField()

    class Meta:
        model = FamilyMember
        fields = [
            'id', 'name', 'age', 'gender', 'relation', 'role', 'is_committee',
            'date_of_birth', 'blood_group', 'phone_no', 'email_id', 'photo',
            'profile_pic', 'bio', 'occupation', 'education', 'parents', 'created_by'
        ]
        extra_kwargs = {
            'parents': {'required': False},
            'created_by': {'read_only': True}
        }

    def get_profile_pic(self, obj):
        if obj.photo:
            return obj.photo.url
        return None

class FamilyTreeSerializer(serializers.ModelSerializer):
    role = serializers.ReadOnlyField()
    is_committee = serializers.ReadOnlyField()

    class Meta:
        model = FamilyMember
        fields = ['id', 'name', 'role', 'is_committee', 'photo', 'parents', 'children']
        depth = 1 

from .models import FamilyMedia
class FamilyMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyMedia
        fields = '__all__'
