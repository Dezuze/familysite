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
             first_name = data.get('first_name', user.username)
             last_name = data.get('last_name', '')
             member = FamilyMember.objects.create(
                 user=user,
                 first_name=first_name,
                 last_name=last_name,
                 gender=data.get('gender', 'M'),
                 date_of_birth=data.get('date_of_birth', '2000-01-01'),
                 blood_group='Unknown', # Default
                 education='',
                 occupation=''
             )

        # Update fields
        if 'first_name' in data: member.first_name = data['first_name']
        if 'last_name' in data: member.last_name = data['last_name']

        if 'nickname' in data: member.nickname = data['nickname']
        
        if 'gender' in data: member.gender = data['gender']
        
        if 'bio' in data: member.bio = data['bio']
        
        if 'date_of_birth' in data: member.date_of_birth = data['date_of_birth']
        if 'education' in data: member.education = data['education']
        if 'occupation' in data: member.occupation = data['occupation']
        if 'place_of_work' in data: member.place_of_work = data['place_of_work']
        if 'blood_group' in data: member.blood_group = data['blood_group']
        if 'address' in data: member.address = data['address']
        
        if 'phone_no' in data: member.phone_no = data['phone_no']
        if 'email_id' in data: member.email_id = data['email_id']
        if 'church_parish' in data: member.church_parish = data['church_parish']
        
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
            full_name = f"{m.first_name} {m.last_name or ''}".strip()
            spouse_name = None
            if m.spouse:
                spouse_name = f"{m.spouse.first_name} {m.spouse.last_name or ''}".strip()

            nodes.append({
                "id": m.id,
                "name": full_name,
                "photo": m.photo.url if m.photo else None,
                "role": "Member",
                "gender": m.gender,
                "username": user_acc.username if user_acc else None,
                "age": age,
                "occupation": m.occupation,
                "date_of_birth": m.date_of_birth,
                "blood_group": m.blood_group,
                "bio": m.bio,
                "education": m.education,
                "location": m.address,
                "place_of_work": m.place_of_work,
                "church_parish": m.church_parish,
                "email_id": m.email_id,
                "phone_no": m.phone_no,
                "is_deceased": m.is_deceased,
                "date_of_death": m.date_of_death,
                "spouse": spouse_name,
                "parents": [{"name": f"{m.parent.first_name} {m.parent.last_name or ''}".strip(), "age": 0}] if m.parent else [],
                "children": [{"name": f"{c.first_name} {c.last_name or ''}".strip(), "age": c.age} for c in FamilyMember.objects.filter(parent=m)],
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
