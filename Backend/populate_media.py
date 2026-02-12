import os
import django
import random
import shutil
from django.core.files import File

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backapi.settings')
django.setup()

from news.models import Post, Media
from profiles.models import Gallery
from families.models import FamilyMember

def populate_media():
    test_dir = r'c:\Users\wesly\OneDrive\Documents\Coding\Project\test'
    images = [f for f in os.listdir(test_dir) if f.endswith('.jpg')]
    
    if not images:
        print("No images found in test directory.")
        return

    # Get a member to be the uploader/creator
    member = FamilyMember.objects.first()
    if not member:
        print("No FamilyMember found to assign as creator.")
        return

    print(f"Using member: {member.name}")

    # 1. Create News Items
    print("Creating News items...")
    news_titles = [
        "Annual Family Gathering 2026",
        "New Educational Achievement in Our Family",
        "Kollamparambil Heritage Site Visit"
    ]
    
    for title in news_titles:
        post = Post.objects.create(
            creator=member,
            post_type='news',
            title=title,
            description="Lending our hearts to tradition and our hands to the future. This is a test post generated for UI verification."
        )
        # Add random image
        img_name = random.choice(images)
        img_path = os.path.join(test_dir, img_name)
        
        with open(img_path, 'rb') as f:
            Media.objects.create(
                uploader=member,
                post=post,
                media_url=File(f, name=img_name),
                media_type='image'
            )
        print(f"  - Created News: {title}")

    # 2. Create Gallery Items
    print("Creating Gallery items...")
    for i, img_name in enumerate(images):
        img_path = os.path.join(test_dir, img_name)
        
        with open(img_path, 'rb') as f:
            gallery_item = Gallery.objects.create(
                date=django.utils.timezone.now().date(),
                description=f"Family Memory #{i+1}"
            )
            gallery_item.image.save(img_name, File(f), save=True)
        print(f"  - Created Gallery item {i+1}: {img_name}")

    print("Success! Test media populated.")

if __name__ == "__main__":
    populate_media()
