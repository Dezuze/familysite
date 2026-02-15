import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backapi.settings')
django.setup()

from families.models import FamilyMember

def debug_aarav_path():
    m = FamilyMember.objects.filter(name__icontains='Aarav').first()
    if m:
        print(f"Name: {m.name}")
        print(f"Photo Relative Path: {m.photo.name}")
        try:
            print(f"Photo Absolute Path: {m.photo.path}")
            print(f"File Exists at Path: {os.path.exists(m.photo.path)}")
        except Exception as e:
            print(f"Error getting path: {e}")
    else:
        print("Aarav not found.")

if __name__ == "__main__":
    debug_aarav_path()
