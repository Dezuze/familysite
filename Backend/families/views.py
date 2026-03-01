"""
Families App Views
==================
REST API endpoints for managing family members, the interactive family tree,
media galleries, and member relationships.

Key Views:
    - UserProfileView: CRUD for the authenticated user's own profile.
    - FamilyTreeView: Builds hierarchical tree data (nodes + links) from
      Relationship records, chaining all relation types into a renderable
      parent/spouse graph for the D3.js frontend.
    - ManagedMembersView: List/create members managed by the current user.
    - FamilyMembersCRUD: Generic detail view for a single member.
    - FamilyMediaCRUD: Gallery list/create and detail endpoints.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import FamilyMember, FamilyMedia, Family, Relationship
from .serializers import FamilyMemberSerializer, FamilyTreeSerializer, FamilyMediaSerializer
from .permissions import IsGuardianOrSelf
from rest_framework import generics
from django.shortcuts import get_object_or_404
from django.db.models import Q
from datetime import date

class UserProfileView(APIView):
    """
    GET  /api/families/profile/  → Return the authenticated user's FamilyMember.
    POST /api/families/profile/  → Create or update the user's profile,
         including demographics, photo, parents (M2M), and relationships.
    """
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
                            auto_gender = Relationship.GENDER_MAP.get(rel_type, 'M')
                            new_member = FamilyMember.objects.create(
                                name=name,
                                relation=rel_type,
                                gender=auto_gender,
                                age=0, 
                                created_by=request.user,
                                family=member.family
                            )
                            to_id = new_member.id
                        elif to_id and rel_type:
                            # Auto-assign gender to existing member if not already set properly
                            auto_gender = Relationship.GENDER_MAP.get(rel_type)
                            if auto_gender:
                                try:
                                    target = FamilyMember.objects.get(id=to_id)
                                    if target.gender != auto_gender:
                                        target.gender = auto_gender
                                        target.save(update_fields=['gender'])
                                except FamilyMember.DoesNotExist:
                                    pass

                        if to_id and rel_type:
                            Relationship.objects.create(
                                from_member=member,
                                to_member_id=to_id,
                                relation_type=rel_type
                            )
                            # Also add to parents M2M for tree compatibility
                            if rel_type in ('Father', 'Mother', 'Grandfather', 'Grandmother',
                                            'Paternal Grandfather', 'Paternal Grandmother',
                                            'Maternal Grandfather', 'Maternal Grandmother'):
                                member.parents.add(to_id)
                            
                            # Handle in-law married_to: create spouse link
                            married_to = item.get('married_to')
                            if married_to and rel_type in ('Sister-in-law', 'Brother-in-law', 'Son-in-law', 'Daughter-in-law'):
                                # Create Spouse relationship between the in-law and the family member
                                Relationship.objects.get_or_create(
                                    from_member_id=married_to,
                                    to_member_id=to_id,
                                    relation_type='Spouse'
                                )
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
    """
    GET /api/families/tree/  → Return { nodes, links } for the D3 tree.

    Link generation algorithm:
        1. Collect all FamilyMembers as nodes.
        2. Convert each Relationship into the correct link type:
           - Father/Mother       → parent link (to_member is parent of from_member)
           - Son/Daughter         → parent link (from_member is parent of to_member)
           - Grandparent variants → chain through Father/Mother as intermediate
           - Siblings             → share parent (both become children of Father)
           - Uncle/Aunt           → child of grandparent (father's sibling)
           - Cousin               → child of uncle/aunt
           - In-laws              → spouse of sibling or parent of spouse
           - Father/Mother-in-law → parent of the user's spouse
           - Nephew/Niece         → child of sibling
        3. Auto-detect co-parents (two parents sharing a child) and add
           spouse links between them.
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        members = FamilyMember.objects.all()
        relationships = Relationship.objects.all()
        
        nodes = []
        links = []
        
        # Track added link pairs to avoid duplicates
        added_links = set()
        
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
            
            # Parent-child links from M2M parents field
            for p in m.parents.all():
                link_key = (p.id, m.id, 'parent')
                if link_key not in added_links:
                    links.append({"source": p.id, "target": m.id, "type": "parent"})
                    added_links.add(link_key)

        # Add all Relationship model links
        # Only Father/Mother create direct "parent" hierarchy links
        # Grandparents chain through Father/Mother when possible
        DIRECT_PARENT_TYPES = {'Father', 'Mother'}
        DIRECT_CHILD_TYPES = {'Son', 'Daughter'}
        GRANDPARENT_TYPES = {'Grandfather', 'Grandmother', 'Paternal Grandfather', 'Paternal Grandmother', 'Maternal Grandfather', 'Maternal Grandmother'}
        GRANDCHILD_TYPES = {'Grandson', 'Granddaughter'}
        SPOUSE_TYPE = {'Spouse'}
        SIBLING_TYPES = {'Brother', 'Sister'}
        IN_LAW_SIBLING_SPOUSE = {
            'Sister-in-law': 'Brother',   # Sister-in-law is brother's wife
            'Brother-in-law': 'Sister',   # Brother-in-law is sister's husband
        }
        
        # First pass: collect who set Father/Mother for whom
        father_of = {}  # member_id -> father_member_id
        mother_of = {}  # member_id -> mother_member_id
        
        for rel in relationships:
            if rel.relation_type == 'Father':
                father_of[rel.from_member_id] = rel.to_member_id
            elif rel.relation_type == 'Mother':
                mother_of[rel.from_member_id] = rel.to_member_id
        
        for rel in relationships:
            from_id = rel.from_member_id
            to_id = rel.to_member_id
            rtype = rel.relation_type
            
            if rtype in DIRECT_PARENT_TYPES:
                # "Alex is my Father" -> Alex is parent of me
                link_key = (to_id, from_id, 'parent')
                if link_key not in added_links:
                    links.append({"source": to_id, "target": from_id, "type": "parent"})
                    added_links.add(link_key)
                    
            elif rtype in DIRECT_CHILD_TYPES:
                # "Bob is my Son" -> I am parent of Bob
                link_key = (from_id, to_id, 'parent')
                if link_key not in added_links:
                    links.append({"source": from_id, "target": to_id, "type": "parent"})
                    added_links.add(link_key)
                    
            elif rtype in GRANDPARENT_TYPES:
                # Chain through correct parent based on side
                # Paternal -> Father, Maternal -> Mother, generic -> first available
                if 'Paternal' in rtype:
                    parent_id = father_of.get(from_id)
                elif 'Maternal' in rtype:
                    parent_id = mother_of.get(from_id)
                else:
                    parent_id = father_of.get(from_id) or mother_of.get(from_id)
                
                if parent_id:
                    link_key = (to_id, parent_id, 'parent')
                    if link_key not in added_links:
                        links.append({"source": to_id, "target": parent_id, "type": "parent"})
                        added_links.add(link_key)
                else:
                    link_key = (to_id, from_id, 'parent')
                    if link_key not in added_links:
                        links.append({"source": to_id, "target": from_id, "type": "parent"})
                        added_links.add(link_key)

            elif rtype in GRANDCHILD_TYPES:
                # "X is my Grandchild" -> I am grandparent, chain through child if known
                link_key = (from_id, to_id, rtype.lower())
                if link_key not in added_links:
                    links.append({"source": from_id, "target": to_id, "type": rtype.lower()})
                    added_links.add(link_key)

            elif rtype in SPOUSE_TYPE:
                pair = tuple(sorted([from_id, to_id]))
                link_key = (pair[0], pair[1], 'spouse')
                if link_key not in added_links:
                    links.append({"source": from_id, "target": to_id, "type": "spouse"})
                    added_links.add(link_key)
                    
            elif rtype in SIBLING_TYPES:
                # Siblings share parents — make them children of the same parent
                # If I have a Father, make Brother also a child of Father
                father_id = father_of.get(from_id)
                mother_id = mother_of.get(from_id)
                
                if father_id:
                    link_key = (father_id, to_id, 'parent')
                    if link_key not in added_links:
                        links.append({"source": father_id, "target": to_id, "type": "parent"})
                        added_links.add(link_key)
                elif mother_id:
                    link_key = (mother_id, to_id, 'parent')
                    if link_key not in added_links:
                        links.append({"source": mother_id, "target": to_id, "type": "parent"})
                        added_links.add(link_key)
                else:
                    # No parent to share, just add sibling link
                    pair = tuple(sorted([from_id, to_id]))
                    link_key = (pair[0], pair[1], 'sibling')
                    if link_key not in added_links:
                        links.append({"source": from_id, "target": to_id, "type": "sibling"})
                        added_links.add(link_key)
            else:
                # Handle in-law types by creating spouse links with siblings
                sibling_match = IN_LAW_SIBLING_SPOUSE.get(rtype)
                if sibling_match:
                    # Find the sibling this in-law is connected to
                    sibling_rel = relationships.filter(
                        from_member_id=from_id, relation_type=sibling_match
                    ).first()
                    if sibling_rel:
                        # Add spouse link: Brother <-> Sister-in-law
                        pair = tuple(sorted([sibling_rel.to_member_id, to_id]))
                        link_key = (pair[0], pair[1], 'spouse')
                        if link_key not in added_links:
                            links.append({"source": sibling_rel.to_member_id, "target": to_id, "type": "spouse"})
                            added_links.add(link_key)

                elif rtype in ('Uncle', 'Aunt'):
                    # Uncle/Aunt = father's/mother's sibling → child of grandparent
                    # Find grandparent (father's father or mother's father)
                    father_id = father_of.get(from_id)
                    mother_id = mother_of.get(from_id)
                    # Check if grandfather/grandmother exists for this person
                    gf_id = None
                    for r in relationships:
                        if r.from_member_id == from_id and r.relation_type in GRANDPARENT_TYPES:
                            gf_id = r.to_member_id
                            break
                    # If no grandparent, try to chain through father's parent
                    if not gf_id and father_id:
                        for r in relationships:
                            if r.to_member_id == father_id and r.relation_type == 'parent':
                                gf_id = r.from_member_id if r.from_member_id != from_id else None
                                if gf_id:
                                    break
                    
                    if gf_id:
                        link_key = (gf_id, to_id, 'parent')
                        if link_key not in added_links:
                            links.append({"source": gf_id, "target": to_id, "type": "parent"})
                            added_links.add(link_key)
                    elif father_id:
                        # Fallback: make uncle sibling of father (child of same parent)
                        # Find any parent link for father
                        for link in links:
                            if link['type'] == 'parent' and link['target'] == father_id:
                                gp_id = link['source']
                                lk = (gp_id, to_id, 'parent')
                                if lk not in added_links:
                                    links.append({"source": gp_id, "target": to_id, "type": "parent"})
                                    added_links.add(lk)
                                break

                elif rtype == 'Cousin':
                    # Cousin = uncle/aunt's child → find uncle/aunt and make cousin their child
                    uncle_rel = relationships.filter(
                        from_member_id=from_id, relation_type__in=['Uncle', 'Aunt']
                    ).first()
                    if uncle_rel:
                        link_key = (uncle_rel.to_member_id, to_id, 'parent')
                        if link_key not in added_links:
                            links.append({"source": uncle_rel.to_member_id, "target": to_id, "type": "parent"})
                            added_links.add(link_key)

                elif rtype in ('Father-in-law', 'Mother-in-law'):
                    # Father-in-law/Mother-in-law = spouse's parent
                    # Find the user's spouse
                    spouse_rel = relationships.filter(
                        from_member_id=from_id, relation_type='Spouse'
                    ).first()
                    if spouse_rel:
                        link_key = (to_id, spouse_rel.to_member_id, 'parent')
                        if link_key not in added_links:
                            links.append({"source": to_id, "target": spouse_rel.to_member_id, "type": "parent"})
                            added_links.add(link_key)

                elif rtype in ('Son-in-law', 'Daughter-in-law'):
                    # Son/Daughter-in-law = child's spouse
                    # Find the child (Son/Daughter) this in-law is married to
                    child_rel = relationships.filter(
                        from_member_id=from_id, relation_type__in=['Son', 'Daughter']
                    ).first()
                    if child_rel:
                        pair = tuple(sorted([child_rel.to_member_id, to_id]))
                        link_key = (pair[0], pair[1], 'spouse')
                        if link_key not in added_links:
                            links.append({"source": child_rel.to_member_id, "target": to_id, "type": "spouse"})
                            added_links.add(link_key)

                elif rtype in ('Nephew', 'Niece'):
                    # Nephew/Niece = sibling's child
                    sibling_rel = relationships.filter(
                        from_member_id=from_id, relation_type__in=['Brother', 'Sister']
                    ).first()
                    if sibling_rel:
                        link_key = (sibling_rel.to_member_id, to_id, 'parent')
                        if link_key not in added_links:
                            links.append({"source": sibling_rel.to_member_id, "target": to_id, "type": "parent"})
                            added_links.add(link_key)

                else:
                    # Truly unknown types - add generic link
                    link_key = (from_id, to_id, rtype)
                    if link_key not in added_links:
                        links.append({"source": from_id, "target": to_id, "type": rtype.lower()})
                        added_links.add(link_key)

        # Auto-detect co-parents (share same child) and add spouse links
        from collections import defaultdict
        children_parents = defaultdict(set)
        for link in links:
            if link['type'] == 'parent':
                children_parents[link['target']].add(link['source'])
        
        for child_id, parent_ids in children_parents.items():
            if len(parent_ids) > 1:
                parent_list = list(parent_ids)
                for i in range(len(parent_list)):
                    for j in range(i + 1, len(parent_list)):
                        pair = tuple(sorted([parent_list[i], parent_list[j]]))
                        link_key = (pair[0], pair[1], 'spouse')
                        if link_key not in added_links:
                            links.append({"source": parent_list[i], "target": parent_list[j], "type": "spouse"})
                            added_links.add(link_key)

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
        # List all members created by this user that are NOT independent
        members = FamilyMember.objects.filter(created_by=request.user, is_independent=False)
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
        member = get_object_or_404(FamilyMember, pk=pk, created_by=user)
        # Enforce guardian permission: can only edit if not independent
        if member.is_independent:
            return None
        return member

    def get(self, request, pk):
        member = get_object_or_404(FamilyMember, pk=pk, created_by=request.user)
        return Response(FamilyMemberSerializer(member).data)

    def put(self, request, pk):
        member = self.get_object(pk, request.user)
        if member is None:
            return Response({"error": "This profile is independent and cannot be edited by the guardian."}, status=403)
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
        if member is None:
            return Response({"error": "This profile is independent and cannot be deleted by the guardian."}, status=403)
        if hasattr(member, 'user_account') and member.user_account:
             return Response({"error": "Member has their own account and cannot be deleted by others."}, status=403)
        member.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
