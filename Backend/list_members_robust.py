import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backapi.settings')
django.setup()

from families.models import FamilyMember

members = FamilyMember.objects.filter(user_account__isnull=True)[:10]
print("START_MEMBERS")
for m in members:
    print(f"ID:{m.id}|Name:{m.name}")
print("END_MEMBERS")
