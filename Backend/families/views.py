from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import FamilyMember, FamilyMedia, Family, Relationship
from .serializers import FamilyMemberSerializer, FamilyTreeSerializer, FamilyMediaSerializer
from rest_framework import generics
from django.shortcuts import get_object_or_404
from django.db.models import Q
from datetime import date

class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        member = FamilyMember.objects.filter(user_account=request.user).first()
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
                     # Fallback: Create a default family if none exists
                     family = Family.objects.create(
                         sl_no="1",
                         branch="Main Branch",
                         member_no="KFA-0001"
                     )
                 
                 dob = data.get('date_of_birth')
                 if not dob:
                     return Response({"error": "Date of birth is required for new profile."}, status=400)
                 
                 # Calculate age
                 try:
                     dob_date = date.fromisoformat(dob)
                     today = date.today()
                     calculated_age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
                 except ValueError:
                     return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

                 member = FamilyMember.objects.create(
                     family=family,
                     name=f"{data.get('first_name', '')} {data.get('last_name', '')}".strip() or user.username,
                     age=calculated_age,
                     date_of_birth=dob_date,
                     blood_group=data.get('blood_group', 'Unknown'),
                     relation='Member'
                 )
                 # Link user to member (since User.member is the field)
                 user.member = member
                 user.save()

            # Update Fields
            if 'first_name' in data or 'last_name' in data:
                f_name = data.get('first_name', '')
                l_name = data.get('last_name', '')
                member.name = f"{f_name} {l_name}".strip()
            elif 'name' in data:
                member.name = data['name']
            
            if 'nickname' in data: member.nickname = data['nickname']
            if 'gender' in data: member.gender = data['gender']
            if 'bio' in data: member.bio = data['bio']
            if 'phone_no' in data: member.phone_no = data['phone_no']
            if 'email_id' in data: member.email_id = data['email_id']
            if 'church_parish' in data: member.church_parish = data['church_parish']
            
            if 'date_of_birth' in data and data['date_of_birth']: 
                dob = data['date_of_birth']
                member.date_of_birth = dob
                # Recalculate age if DOB changed
                try:
                    dob_date = date.fromisoformat(dob)
                    today = date.today()
                    member.age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
                except (ValueError, TypeError):
                    pass

            if 'education' in data: member.education = data['education']
            if 'occupation' in data: member.occupation = data['occupation']
            if 'place_of_work' in data: member.place_of_work = data['place_of_work']
            if 'blood_group' in data: member.blood_group = data['blood_group']
            if 'is_deceased' in data: member.is_deceased = data['is_deceased'] == 'true' or data['is_deceased'] == True
            if 'address' in data: member.address_if_different = data['address']
            elif 'address_if_different' in data: member.address_if_different = data['address_if_different']
            
            # Update Parents (ManyToMany)
            if 'parents' in data:
                # Handle FormData getlist or JSON list
                if hasattr(data, 'getlist'):
                    parent_ids = data.getlist('parents')
                else:
                    parent_ids = data['parents']
                
                if isinstance(parent_ids, str):
                    parent_ids = [p.strip() for p in parent_ids.split(',')]
                
                member.parents.set(parent_ids)
            
            # Update Relationships
            if 'relationships' in data:
                import json
                try:
                    rel_data = data['relationships']
                    if isinstance(rel_data, str):
                        rel_data = json.loads(rel_data)
                    
                    # Clear existing and re-add? Or just add new ones?
                    # For onboarding, clearing might be cleaner
                    Relationship.objects.filter(from_member=member).delete()
                    for item in rel_data:
                        to_id = item.get('to_member') or item.get('to_member_id')
                        rel_type = item.get('relation_type')
                        name = item.get('name') or item.get('to_member_name')
                        
                        if not to_id and name:
                            # Auto-create member if not found
                            new_member = FamilyMember.objects.create(
                                name=name,
                                relation=rel_type, # Temporary
                                age=0, 
                                created_by=request.user,
                                family=member.family
                            )
                            to_id = new_member.id

                        if to_id and rel_type:
                            Relationship.objects.create(
                                from_member=member,
                                to_member_id=to_id,
                                relation_type=rel_type
                            )
                            # Special case: Father/Mother also go to parents M2M for tree
                            if rel_type in ['Father', 'Mother']:
                                member.parents.add(to_id)
                except Exception as e:
                    print(f"Error saving relationships: {e}")

            # Update Profile Pic
            if 'profile_pic' in request.FILES:
                member.photo = request.FILES['profile_pic']
            elif 'photo' in request.FILES:
                member.photo = request.FILES['photo']
            
            member.save()
            
            return Response(FamilyMemberSerializer(member).data)
        except Exception as e:
            import traceback
            traceback.print_exc() # Print to server logs for debugging
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
                "role": m.role,
                "is_committee": m.is_committee,
                "username": username,
                "gender": m.gender,
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
        serializer.save()

class FamilyMediaDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = FamilyMedia.objects.all()
    serializer_class = FamilyMediaSerializer
    permission_classes = [permissions.IsAuthenticated]

class ManagedMembersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # List all members created by this user
        members = FamilyMember.objects.filter(created_by=request.user)
        serializer = FamilyMemberSerializer(members, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Create a new member managed by this user
        try:
            data = request.data
            from .models import Family
            family = Family.objects.first()
            if not family:
                return Response({"error": "No family found"}, status=400)

            # Extract fields
            f_name = data.get('first_name', '')
            l_name = data.get('last_name', '')
            full_name = data.get('name', f"{f_name} {l_name}".strip())

            member = FamilyMember.objects.create(
                family=family,
                name=full_name,
                age=data.get('age', 0),
                gender=data.get('gender', 'M'),
                relation=data.get('relation', 'Child'),
                date_of_birth=data.get('date_of_birth', '2000-01-01'),
                blood_group=data.get('blood_group', 'Unknown'),
                occupation=data.get('occupation', ''),
                education=data.get('education', ''),
                is_deceased=data.get('is_deceased', 'false') == 'true' or data.get('is_deceased') == True,
                phone_no=data.get('phone_no', ''),
                email_id=data.get('email_id', ''),
                address_if_different=data.get('address', ''),
                bio=data.get('bio', ''),
                church_parish=data.get('church_parish', ''),
                nickname=data.get('nickname', ''),
                created_by=request.user
            )

            # Link parents if provided
            if 'parents' in data:
                if hasattr(data, 'getlist'):
                    parent_ids = data.getlist('parents')
                else:
                    parent_ids = data['parents']
                
                if isinstance(parent_ids, str):
                    parent_ids = [p.strip() for p in parent_ids.split(',')]
                member.parents.set(parent_ids)

            # Relationships
            if 'relationships' in data:
                import json
                try:
                    rel_data = data['relationships']
                    if isinstance(rel_data, str):
                        rel_data = json.loads(rel_data)
                    for item in rel_data:
                        to_id = item.get('to_member') or item.get('to_member_id')
                        rel_type = item.get('relation_type')
                        name = item.get('name') or item.get('to_member_name')

                        if not to_id and name:
                            # Auto-create member if not found
                            new_member = FamilyMember.objects.create(
                                name=name,
                                relation=rel_type, # Temporary
                                age=0, 
                                created_by=request.user,
                                family=member.family
                            )
                            to_id = new_member.id

                        if to_id and rel_type:
                            Relationship.objects.create(
                                from_member=member,
                                to_member_id=to_id,
                                relation_type=rel_type
                            )
                            if rel_type in ['Father', 'Mother']:
                                member.parents.add(to_id)
                except Exception as e:
                    print(f"Error saving relationships: {e}")

            # Profile Pic
            if 'profile_pic' in request.FILES:
                member.photo = request.FILES['profile_pic']
            elif 'photo' in request.FILES:
                member.photo = request.FILES['photo']
            
            member.save()

            return Response(FamilyMemberSerializer(member).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

class ManagedMemberDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk, user):
        return get_object_or_404(FamilyMember, pk=pk, created_by=user)

    def get(self, request, pk):
        member = self.get_object(pk, request.user)
        return Response(FamilyMemberSerializer(member).data)

    def put(self, request, pk):
        member = self.get_object(pk, request.user)
        # Prevent editing if the member has their own account now?
        # The user said "if there isnt an account for them".
        if hasattr(member, 'user_account') and member.user_account:
             return Response({"error": "Member has their own account and cannot be managed by others."}, status=403)

        try:
            data = request.data
            
            f_name = data.get('first_name')
            l_name = data.get('last_name')
            if f_name is not None or l_name is not None:
                member.name = f"{f_name or ''} {l_name or ''}".strip()
            elif 'name' in data:
                member.name = data['name']

            if 'age' in data: member.age = data['age']
            if 'gender' in data: member.gender = data['gender']
            if 'relation' in data: member.relation = data['relation']
            if 'date_of_birth' in data: member.date_of_birth = data['date_of_birth']
            if 'blood_group' in data: member.blood_group = data['blood_group']
            if 'occupation' in data: member.occupation = data['occupation']
            if 'education' in data: member.education = data['education']
            if 'phone_no' in data: member.phone_no = data['phone_no']
            if 'email_id' in data: member.email_id = data['email_id']
            if 'is_deceased' in data: member.is_deceased = data['is_deceased'] == 'true' or data['is_deceased'] == True
            if 'address' in data: member.address_if_different = data['address']
            if 'bio' in data: member.bio = data['bio']
            if 'nickname' in data: member.nickname = data['nickname']
            if 'church_parish' in data: member.church_parish = data['church_parish']

            # Relationships
            if 'relationships' in data:
                import json
                try:
                    rel_data = data['relationships']
                    if isinstance(rel_data, str):
                        rel_data = json.loads(rel_data)
                    
                    Relationship.objects.filter(from_member=member).delete()
                    for item in rel_data:
                        to_id = item.get('to_member') or item.get('to_member_id')
                        rel_type = item.get('relation_type')
                        name = item.get('name') or item.get('to_member_name')

                        if not to_id and name:
                            # Auto-create member if not found
                            new_member = FamilyMember.objects.create(
                                name=name,
                                relation=rel_type, # Temporary
                                age=0, 
                                created_by=request.user,
                                family=member.family
                            )
                            to_id = new_member.id

                        if to_id and rel_type:
                            Relationship.objects.create(
                                from_member=member,
                                to_member_id=to_id,
                                relation_type=rel_type
                            )
                            if rel_type in ['Father', 'Mother']:
                                member.parents.add(to_id)
                except Exception as e:
                    print(f"Error saving relationships: {e}")

            if 'parents' in data:
                if hasattr(data, 'getlist'):
                    parent_ids = data.getlist('parents')
                else:
                    parent_ids = data['parents']
                
                if isinstance(parent_ids, str):
                    parent_ids = [p.strip() for p in parent_ids.split(',')]
                member.parents.set(parent_ids)

            if 'profile_pic' in request.FILES:
                member.photo = request.FILES['profile_pic']
            elif 'photo' in request.FILES:
                member.photo = request.FILES['photo']

            member.save()
            return Response(FamilyMemberSerializer(member).data)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    def delete(self, request, pk):
        member = self.get_object(pk, request.user)
        if hasattr(member, 'user_account') and member.user_account:
             return Response({"error": "Member has their own account and cannot be deleted by others."}, status=403)
        member.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
