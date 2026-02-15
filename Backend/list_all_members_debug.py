import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backapi.settings')
django.setup()

from families.models import FamilyMember

def list_all_members():
    members = FamilyMember.objects.all().order_by('id')
    for m in members:
        print(f"ID: {m.id}, Name: {m.name}, Photo: {m.photo.name if m.photo else 'None'}")

if __name__ == "__main__":
    list_all_members()
