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
             name = f"{data.get('first_name', user.username)} {data.get('last_name', '')}".strip()
             member = FamilyMember.objects.create(
                 user=user,
                 name=name,
                 gender=data.get('gender', 'M'),
                 age=0, # Default
                 date_of_birth='2000-01-01', # Default
                 relation='Self', # Default
                 blood_group='Unknown', # Default
                 education='',
                 occupation=''
             )

        # Update fields
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        if first_name or last_name:
            # If only one provided, we might need to be careful, but assuming frontend sends both
            current_names = member.name.split(' ') if member.name else ["", ""]
            new_first = first_name if first_name is not None else (current_names[0] if current_names else "")
            new_last = last_name if last_name is not None else (" ".join(current_names[1:]) if len(current_names) > 1 else "")
            member.name = f"{new_first} {new_last}".strip()

        if 'nickname' in data: member.nickname = data['nickname']
        
        if 'gender' in data: member.gender = data['gender']
        
        if 'bio' in data: member.bio = data['bio']
        
        if 'date_of_birth' in data: member.date_of_birth = data['date_of_birth']
        if 'education' in data: member.education = data['education']
        if 'occupation' in data: member.occupation = data['occupation']
        if 'place_of_work' in data: member.place_of_work = data['place_of_work']
        if 'blood_group' in data: member.blood_group = data['blood_group']
        if 'address' in data: member.address_if_different = data['address']
        
        if 'phone_no' in data: member.phone_no = data['phone_no']
        if 'email_id' in data: member.email_id = data['email_id']
        if 'church_parish' in data: member.church_parish = data['church_parish']
        
        # Update Profile Pic
        if 'profile_pic' in request.FILES:
            member.photo = request.FILES['profile_pic'] # Model has 'photo', view was using 'profile_pic'
        
        member.save()
        
        return Response(FamilyMemberSerializer(member).data)


class FamilyTreeView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        members = FamilyMember.objects.all()
        
        nodes = []
        links = []
        
        for m in members:
            # Calculate Age
            age = 0
            if m.date_of_birth:
                today = date.today()
                dob = m.date_of_birth
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if m.is_deceased and m.date_of_death:
                 # Age at death
                 drun = m.date_of_death
                 age = drun.year - m.date_of_birth.year - ((drun.month, drun.day) < (m.date_of_birth.month, m.date_of_birth.day))

            user_acc = getattr(m, 'user_account', None)
            
            nodes.append({
                "id": m.id,
                "name": m.name, # Property
                "photo": m.profile_pic.url if m.profile_pic else None,
                "role": "Member", # Default, or derive 'Father'/'Son' via tree traversal if needed? Frontend card uses 'relation'. Using 'Member' for now.
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
                "spouse": m.spouse.name if m.spouse else None,
                "parents": [{"name": p.first_name, "age": 0} for p in m.parents.all()],
                "children": [{"name": c.first_name, "age": c.age} for c in FamilyMember.objects.filter(parent=m)],
                "is_committee": user_acc.committee_entries.exists() if user_acc else False,
                "committee_role": user_acc.committee_entries.first().role if (user_acc and user_acc.committee_entries.exists()) else None
            })
            
            # Spouse link
            if m.spouse:
                if m.id < m.spouse.id:
                    links.append({"source": m.id, "target": m.spouse.id, "type": "spouse"})

            # Parent child link
            # Use 'parent' FK (Tree) and 'parents' M2M (Bio) -> User wants Tree primarily?
            # User request: "Points to the parent member... Recursive self-reference".
            # If I use 'parent' FK, I get a clear tree.
            if m.parent:
                 links.append({"source": m.parent.id, "target": m.id, "type": "parent"})
            
            # Also legacy parents M2M?
            for p in m.parents.all():
                 # Avoid duplicating if same as parent FK
                 if not m.parent or p.id != m.parent.id:
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
