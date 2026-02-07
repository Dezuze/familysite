from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from families.models import FamilyMember
from profiles.models import Committee
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed committee members with roles'

    def handle(self, *args, **options):
        # clear existing
        Committee.objects.all().delete()
        
        roles = [
            'Patron',
            'President',
            'Vice President',
            'Secretary',
            'Joint Secretary',
            'Treasurer',
            'Committee Member',
            'Committee Member',
            'Committee Member',
            'Committee Member',
        ]
        
        members = list(FamilyMember.objects.all())
        if not members:
            self.stdout.write(self.style.ERROR('No family members found to seed'))
            return

        roles_needed = len(roles)
        if len(members) < roles_needed:
             # Just cycle members if not enough
             import itertools
             members = list(itertools.islice(itertools.cycle(members), roles_needed))
        
        # Shuffle members to pick refreshing random candidates each time
        random.shuffle(members)
        
        for i, role in enumerate(roles):
            try:
                member = members[i]
                
                # Ensure member has a User account
                user = None
                if hasattr(member, 'user_account'):
                    user = member.user_account
                else:
                    username = f'comm_user_{member.id}'
                    # Check if username exists (unlikely if unique member logic holds, but safe check)
                    if User.objects.filter(username=username).exists():
                         user = User.objects.get(username=username)
                         # link if not linked
                         if not user.member:
                             user.member = member
                             user.save()
                    else:
                         user = User.objects.create_user(
                            username=username, 
                            email=f'{username}@example.com',
                            password='password123'
                         )
                         user.member = member
                         user.save()
                
                # Create Committee Entry
                Committee.objects.create(
                    user=user,
                    role=role,
                    pic=member.photo if member.photo else None 
                )
                # Use property name or first_name
                member_name = member.name
                self.stdout.write(f'Assigned {member_name} as {role}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error assigning {role}: {e}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {len(roles)} committee members.'))
