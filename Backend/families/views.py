from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import FamilyMember, FamilyMedia
from .serializers import FamilyMemberSerializer, FamilyTreeSerializer, FamilyMediaSerializer
from rest_framework import generics
from django.shortcuts import get_object_or_404
from django.db.models import Q
from datetime import date

class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        member = FamilyMember.objects.filter(user=request.user).first()
        if member:
            serializer = FamilyMemberSerializer(member)
            return Response(serializer.data)
        return Response({"error": "Profile not linked"}, status=404)

    def post(self, request):
        data = request.data
        user = request.user
        
        # Check if member exists
        member = FamilyMember.objects.filter(user=user).first()
        
        if not member:
             # Create new member if not exists
             # Create new member if not exists
             name = data.get('name', user.username)
             member = FamilyMember.objects.create(
                 user=user,
                 name=name,
                 date_of_birth=data.get('date_of_birth', '2000-01-01'),
                 blood_group='U', # Default (fits in max_length=5)
                 education='',
                 occupation=''
             )

        # Update fields
        if 'name' in data: member.name = data['name']
        
        if 'date_of_birth' in data: member.date_of_birth = data['date_of_birth']
        if 'education' in data: member.education = data['education']
        if 'occupation' in data: member.occupation = data['occupation']
        if 'place_of_work' in data: member.place_of_work = data['place_of_work']
        if 'blood_group' in data: member.blood_group = data['blood_group']
        if 'address' in data: member.address_if_different = data['address']
        
        # Update Profile Pic
        if 'profile_pic' in request.FILES:
            member.photo = request.FILES['profile_pic']
        
        member.save()
        
        return Response(FamilyMemberSerializer(member).data)


class FamilyTreeView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        members = FamilyMember.objects.all()
        
        nodes = []
        links = []
        
        for m in members:
            # Calculate Age using property
            age = m.age

            user_acc = getattr(m, 'user_account', None)
            
            # Combine name
            # Combine name
            full_name = m.name
            spouse_name = None
            if m.spouse:
                spouse_name = m.spouse.name

            nodes.append({
                "id": m.id,
                "name": full_name,
                "photo": m.photo.url if m.photo else None,
                "role": "Member",
                "username": user_acc.username if user_acc else None,
                "age": age,
                "occupation": m.occupation,
                "date_of_birth": m.date_of_birth,
                "blood_group": m.blood_group,
                "education": m.education,
                "location": m.address_if_different,
                "place_of_work": m.place_of_work,
                "spouse": spouse_name,
                "parents": [{"name": p.name, "age": 0} for p in m.parents.all()],
                "children": [{"name": c.name, "age": c.age} for c in m.children.all()],
                "is_committee": user_acc.committee_entries.exists() if user_acc else False,
                "committee_role": user_acc.committee_entries.first().role if (user_acc and user_acc.committee_entries.exists()) else None
            })
            
            # Spouse link
            if m.spouse:
                if m.id < m.spouse.id:
                    links.append({"source": m.id, "target": m.spouse.id, "type": "spouse"})

            # Parent child link (Tree)
            if m.parent:
                 links.append({"source": m.parent.id, "target": m.id, "type": "parent"})

        return Response({"nodes": nodes, "links": links})


class FamilyMediaList(generics.ListCreateAPIView):
    queryset = FamilyMedia.objects.all()
    serializer_class = FamilyMediaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Determine family? The serializer expects 'family' field or we derive it?
        # The test sends 'family' ID in data. So serializer handles it.
        serializer.save()

class FamilyMediaDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = FamilyMedia.objects.all()
    serializer_class = FamilyMediaSerializer
    permission_classes = [permissions.IsAuthenticated]
