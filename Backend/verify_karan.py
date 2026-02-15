import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backapi.settings')
django.setup()

from families.models import FamilyMember
from accounts.models import User

try:
    u = User.objects.get(username='karan_secretary')
    m = FamilyMember.objects.get(id=141)
    print(f"User: {u.username}")
    print(f"Linked Member: {m.name} (ID: {m.id})")
    print(f"Role Property: {m.role}")
    print(f"Is Committee: {m.is_committee}")
except Exception as e:
    print(f"Error: {e}")
