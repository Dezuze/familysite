import os
import django
import random
import shutil
from django.core.files import File

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backapi.settings')
django.setup()

from families.models import FamilyMember

def bulk_assign_avatars():
    avatar_dir = r'c:\Users\wesly\OneDrive\Documents\Coding\Project\backend\media\avatars'
    
    # Get all avatar files
    avatars = [f for f in os.listdir(avatar_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
    
    if not avatars:
        print("No avatars found in media/avatars.")
        return

    # Filter by gender if possible, but let's just use random for simplicity first
    # Or try a basic heuristic
    female_names = ['amanda', 'deborah', 'jill', 'julie', 'kathy', 'sarah', 'tina']
    male_names = ['bernard', 'matthew', 'peter', 'richard', 'shawn', 'stephen']
    
    female_avatars = [a for a in avatars if any(name in a.lower() for name in female_names)]
    male_avatars = [a for a in avatars if any(name in a.lower() for name in male_names)]
    general_avatars = [a for a in avatars if a not in female_avatars and a not in male_avatars]

    members_to_update = FamilyMember.objects.filter(models.Q(photo='') | models.Q(photo=None))
    
    print(f"Assigning avatars to {members_to_update.count()} members...")
    
    for member in members_to_update:
        # Choose pool based on gender
        if member.gender == 'F' and female_avatars:
            pool = female_avatars
        elif member.gender == 'M' and male_avatars:
            pool = male_avatars
        else:
            pool = general_avatars if general_avatars else avatars
            
        avatar_name = random.choice(pool)
        avatar_path = os.path.join(avatar_dir, avatar_name)
        
        with open(avatar_path, 'rb') as f:
            member.photo.save(avatar_name, File(f), save=True)
        
        print(f"  - Assigned {avatar_name} to {member.name} ({member.gender})")

    print("Success! Bulk avatar assignment complete.")

if __name__ == "__main__":
    from django.db import models
    bulk_assign_avatars()
