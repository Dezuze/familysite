import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backapi.settings')
django.setup()

from families.models import FamilyMember
from profiles.models import Committee
from accounts.models import User

try:
    m = FamilyMember.objects.get(id=141)
    c = Committee.objects.filter(user__username='karan_secretary').first()
    
    print("---DATA_CHECK---")
    print(f"FamilyMember_Photo: {m.photo}")
    print(f"Committee_Pic: {c.pic if c else None}")
    
    # If missing on member, assign one
    if not m.photo:
        m.photo = 'avatars/avatar_shawn281.jpg'
        m.save()
        print("Set photo on FamilyMember.")
    
    # Ensure committee pic is also set
    if c and not c.pic:
        c.pic = 'committee/avatar_shawn281.jpg'
        c.save()
        print("Set pic on Committee.")
        
    print("---FINAL_STATE---")
    m.refresh_from_db()
    print(f"M_PHOTO: {m.photo}")
    if c:
        c.refresh_from_db()
        print(f"C_PIC: {c.pic}")
    print("---END---")

except Exception as e:
    print(f"Error: {e}")
