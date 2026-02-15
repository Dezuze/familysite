from families.models import FamilyMember
from accounts.models import User

members = FamilyMember.objects.filter(user_account__isnull=True)
print("START_MEMBERS")
for m in members[:10]:
    print(f"ID:{m.id}|Name:{m.name}")
print("END_MEMBERS")
