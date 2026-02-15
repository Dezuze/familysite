import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backapi.settings')
django.setup()

from families.models import FamilyMember
from accounts.models import User
from profiles.models import Committee

try:
    # Create user
    username = 'karan_secretary'
    email = 'karan@example.com'
    password = 'FamilyTest2026!'
    
    if not User.objects.filter(username=username).exists():
        u = User.objects.create_user(username=username, email=email, password=password)
        print(f"User {username} created.")
    else:
        u = User.objects.get(username=username)
        print(f"User {username} already exists.")
        
    # Link to member
    m = FamilyMember.objects.get(id=141)
    u.member = m
    u.save()
    print(f"User linked to member {m.name} (ID: {m.id}).")
    
    # Assign Secretary role
    if not Committee.objects.filter(user=u, role='Secretary').exists():
        Committee.objects.create(user=u, role='Secretary', pic='committee/avatar_shawn281.jpg')
        print("Secretary role assigned.")
    else:
        print("Secretary role already assigned.")
        
except Exception as e:
    print(f"Error: {e}")
