from rest_framework import serializers
from .models import FamilyMember, Relationship

class RelationshipSerializer(serializers.ModelSerializer):
    to_member_name = serializers.CharField(source='to_member.name', read_only=True)
    
    class Meta:
        model = Relationship
        fields = ['id', 'to_member', 'to_member_name', 'relation_type']

class FamilyMemberSerializer(serializers.ModelSerializer):
    role = serializers.ReadOnlyField()
    is_committee = serializers.ReadOnlyField()
    profile_pic = serializers.SerializerMethodField()
    has_account = serializers.SerializerMethodField()
    relationships = RelationshipSerializer(source='relationships_from', many=True, read_only=True)

    class Meta:
        model = FamilyMember
        fields = [
            'id', 'name', 'nickname', 'age', 'gender', 'relation', 'role', 'is_committee',
            'date_of_birth', 'date_of_death', 'blood_group', 'is_deceased', 'is_independent', 'has_account',
            'phone_no', 'email_id', 'photo',
            'profile_pic', 'bio', 'occupation', 'education', 'address_if_different', 
            'place_of_work', 'church_parish', 'parents', 'created_by', 'relationships'
        ]
        extra_kwargs = {
            'parents': {'required': False},
            'created_by': {'read_only': True},
            'date_of_birth': {'required': False, 'allow_null': True},
            'date_of_death': {'required': False, 'allow_null': True},
        }

    def get_profile_pic(self, obj):
        if obj.photo:
            return obj.photo.url
        return None

    def get_has_account(self, obj):
        return hasattr(obj, 'user_account') and obj.user_account is not None

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
