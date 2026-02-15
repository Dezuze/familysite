import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backapi.settings')
django.setup()

from families.models import FamilyMember

def debug_aarav():
    m = FamilyMember.objects.filter(name__icontains='Aarav').first()
    if m:
        print(f"Name: {m.name}")
        print(f"Photo Field: '{m.photo}'")
        print(f"Photo Bool: {bool(m.photo)}")
        if m.photo:
            print(f"Photo URL: {m.photo.url}")
            print(f"File Exists: {os.path.exists(m.photo.path) if hasattr(m.photo, 'path') else 'N/A'}")
    else:
        print("Aarav not found.")

if __name__ == "__main__":
    debug_aarav()
