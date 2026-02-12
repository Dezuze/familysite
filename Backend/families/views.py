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
            
            # Check if member exists via OneToOne relationship
            member = getattr(user, 'member', None)
            
            if not member:
                 # Create new member if not exists - needs a family
                 family = Family.objects.first()
                 if not family:
                     return Response({"error": "No families found in database. Contact admin."}, status=400)
                     
                 member = FamilyMember.objects.create(
                     family=family,
                     name=f"{data.get('first_name', '')} {data.get('last_name', '')}".strip() or user.username,
                     age=30,
                     date_of_birth=data.get('date_of_birth', '1994-01-01'),
                     blood_group='O+',
                     relation='Member'
                 )
                 # Link user to member (since User.member is the field)
                 user.member = member
                 user.save()

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
            
            # Update Parents (ManyToMany)
            if 'parents' in data:
                parent_ids = data['parents']
                if isinstance(parent_ids, str):
                    # Handle comma separated string if sent that way
                    parent_ids = [p.strip() for p in parent_ids.split(',')]
                member.parents.set(parent_ids)
            
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
        
        processed_spouses = set()
        for m in members:
            # Username for centering focus
            username = None
            if hasattr(m, 'user_account'):
                username = m.user_account.username

            nodes.append({
                "id": m.id,
                "name": m.name,
                "photo": m.photo.url if m.photo else None,
                "role": "Member",
                "username": username,
                "gender": "M" if "Son" in (m.relation or "") or "Head" in (m.relation or "") and "Widow" not in (m.relation or "") else "F",
                "age": m.age,
                "occupation": m.occupation,
                "date_of_birth": m.date_of_birth,
                "blood_group": m.blood_group,
                "education": m.education,
                "location": m.address_if_different,
                "place_of_work": m.place_of_work,
            })
            
            # Parent-child links
            for p in m.parents.all():
                 links.append({"source": p.id, "target": m.id, "type": "parent"})

            # Spouse Detection: Share the same children
            children_ids = set(m.children.values_list('id', flat=True))
            if children_ids:
                # Find other parents of these children
                other_parents = FamilyMember.objects.filter(children__id__in=children_ids).exclude(id=m.id).distinct()
                for op in other_parents:
                    spouse_pair = tuple(sorted([m.id, op.id]))
                    if spouse_pair not in processed_spouses:
                        links.append({"source": m.id, "target": op.id, "type": "spouse"})
                        processed_spouses.add(spouse_pair)

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
