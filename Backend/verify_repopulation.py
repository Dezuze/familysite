import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backapi.settings')
django.setup()

from families.models import FamilyMember

def verify_repopulation():
    print(f"Total Members: {FamilyMember.objects.count()}")
    print(f"Members with Photos: {FamilyMember.objects.exclude(photo='').count()}")
    
    m = FamilyMember.objects.first()
    if m:
        print(f"Sample Member: {m.name}")
        print(f"Photo Name: {m.photo.name}")
        print(f"Photo URL: {m.photo.url if m.photo else 'None'}")
        if m.photo:
            print(f"Physical File Exists: {os.path.exists(m.photo.path)}")
    else:
        print("No members found!")

if __name__ == "__main__":
    verify_repopulation()
