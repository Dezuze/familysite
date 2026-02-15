import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backapi.settings')
django.setup()

from families.models import FamilyMember

def check_avatars():
    members = FamilyMember.objects.all()
    total = members.count()
    with_photo = members.exclude(photo='').exclude(photo=None).count()
    
    print(f"Total members: {total}")
    print(f"Members with photo: {with_photo}")
    
    if with_photo > 0:
        first_with_photo = members.exclude(photo='').exclude(photo=None).first()
        print(f"Sample photo path: {first_with_photo.photo.name}")
        print(f"Sample photo URL: {first_with_photo.photo.url if hasattr(first_with_photo.photo, 'url') else 'N/A'}")

if __name__ == "__main__":
    check_avatars()
