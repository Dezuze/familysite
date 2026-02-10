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
        try:
            data = request.data
            user = request.user
            
            # Check if member exists
            member = FamilyMember.objects.filter(user=user).first()
            
            if not member:
                 # Create new member if not exists - needs a family
                 family = Family.objects.first()
                 if not family:
                     return Response({"error": "No families found in database. Contact admin."}, status=400)
                     
                 member = FamilyMember.objects.create(
                     user=user,
                     family=family,
                     name=f"{data.get('first_name', '')} {data.get('last_name', '')}".strip() or user.username,
                     age=30,
                     date_of_birth=data.get('date_of_birth', '1994-01-01'),
                     blood_group='O+',
                     relation='Member'
                 )

            # Update Name from split fields if provided
            if 'first_name' in data or 'last_name' in data:
                f_name = data.get('first_name', '')
                l_name = data.get('last_name', '')
                member.name = f"{f_name} {l_name}".strip()
            elif 'name' in data:
                member.name = data['name']
            
            if 'date_of_birth' in data: member.date_of_birth = data['date_of_birth']
            if 'education' in data: member.education = data['education']
            if 'occupation' in data: member.occupation = data['occupation']
            if 'place_of_work' in data: member.place_of_work = data['place_of_work']
            if 'blood_group' in data: member.blood_group = data['blood_group']
            if 'address' in data: member.address_if_different = data['address']
            
            # Additional fields sent by frontend
            # Note: You might want to add these to the model if they are missing
            # For now we'll handle what exists and ignore the rest safely
            
            # Update Profile Pic
            if 'profile_pic' in request.FILES:
                member.photo = request.FILES['profile_pic']
            
            member.save()
            
            return Response(FamilyMemberSerializer(member).data)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class FamilyTreeView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        members = FamilyMember.objects.all()
        
        nodes = []
        links = []
        
        for m in members:
            # Combine name
            full_name = m.name

            nodes.append({
                "id": m.id,
                "name": full_name,
                "photo": m.photo.url if m.photo else None,
                "role": "Member",
                "username": m.user.username if m.user else None,
                "age": m.age,
                "occupation": m.occupation,
                "date_of_birth": m.date_of_birth,
                "blood_group": m.blood_group,
                "education": m.education,
                "location": m.address_if_different,
                "place_of_work": m.place_of_work,
                "parents": [{"name": p.name, "age": p.age} for p in m.parents.all()],
                "children": [{"name": c.name, "age": c.age} for c in m.children.all()],
            })
            
            # Parent-child links (Tree) using ManyToMany
            for p in m.parents.all():
                 links.append({"source": p.id, "target": m.id, "type": "parent"})

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
