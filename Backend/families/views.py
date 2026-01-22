from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import FamilyMember
from .serializers import FamilyMemberSerializer, FamilyTreeSerializer
from django.shortcuts import get_object_or_404
from django.db.models import Q

class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Find the FamilyMember linked to this user
        # IF not found, maybe return 404 or empty structure
        try:
            member = FamilyMember.objects.get(user=request.user)
            serializer = FamilyMemberSerializer(member)
            return Response(serializer.data)
        except FamilyMember.DoesNotExist:
            return Response({"error": "Profile not linked"}, status=404)

    def post(self, request):
        # Update or Create profile details
        # Expecting full details: name, dob, father_name (to lookup or create), mother_name, etc.
        data = request.data
        user = request.user
        
        # Check if member exists
        member, created = FamilyMember.objects.get_or_create(user=user, defaults={
            'name': user.first_name or user.username,
            'age': 0,
            'blood_group': 'Unknown',
            'date_of_birth': '2000-01-01',
            'education': '',
            'occupation': '',
        })

        # Update simple fields
        if 'name' in data: member.name = data['name']
        if 'bio' in data: member.bio = data['bio']
        if 'date_of_birth' in data: member.date_of_birth = data['date_of_birth']
        if 'age' in data: member.age = data['age']
        if 'education' in data: member.education = data['education']
        if 'occupation' in data: member.occupation = data['occupation']
        if 'blood_group' in data: member.blood_group = data['blood_group']
        if 'address_if_different' in data: member.address_if_different = data['address_if_different']

        # Update User Avatar if provided
        # (Handling FormData, 'avatar' key)
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
            user.save()
        elif 'avatar' in data and data['avatar']:
            # If it's sent as not a file (rare with formData but possible)
             pass

        # Handle parents logic (simplistic text lookup or ID link)
        # For a real app, you'd search by ID or strict Name+DOB. 
        # Here we just look for existing unlinked members by name or create ghosts.
        
        # Save first to ensure ID
        member.save()
        
        return Response(FamilyMemberSerializer(member).data)


class FamilyTreeView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        # Return all nodes and links for D3
        members = FamilyMember.objects.all()
        
        nodes = []
        links = []
        
        for m in members:
            nodes.append({
                "id": m.id,
                "name": m.name,
                "photo": m.photo.url if m.photo else None,
                "role": "Member", # could be dynamic
                "username": m.user.username if m.user else None
            })
            
            # Spouse link
            if m.spouse:
                # To avoid double link, only add if m.id < spouse.id
                if m.id < m.spouse.id:
                    links.append({"source": m.id, "target": m.spouse.id, "type": "spouse"})

            # Parent child link
            # parents is ManyToMany.
            for p in m.parents.all():
                 links.append({"source": p.id, "target": m.id, "type": "parent"})

        return Response({"nodes": nodes, "links": links})
