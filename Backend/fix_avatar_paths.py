import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backapi.settings')
django.setup()

from families.models import FamilyMember

def fix_avatar_paths():
    members = FamilyMember.objects.all()
    count = 0
    for m in members:
        if m.photo and not m.photo.name.startswith(('avatars/', 'members/photos/')):
            # The file is in media/avatars/
            m.photo.name = f"avatars/{m.photo.name}"
            m.save()
            count += 1
    print(f"Fixed paths for {count} members.")

if __name__ == "__main__":
    fix_avatar_paths()
