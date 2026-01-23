import random
import io
import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.utils import timezone
from PIL import Image
from faker import Faker

# Import models
from families.models import Family, FamilyHead, FamilyMember, DeceasedMember, FamilyMedia
from news.models import News
from profiles.models import Gallery, Committee

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with 30+ entries for each table using correct models.'

    def handle(self, *args, **options):
        self.stdout.write('Starting Single Connected Family Tree Seeding...')
        fake = Faker()

        # Helper to generate images
        def generate_image(width=640, height=480, color=None):
            if color is None:
                color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            image = Image.new('RGB', (width, height), color)
            img_io = io.BytesIO()
            image.save(img_io, format='JPEG')
            return ContentFile(img_io.getvalue(), name=f'seed_{random.randint(1000, 9999)}.jpg')

        # 1. Cleanup
        self.stdout.write('Cleaning up old data...')
        Committee.objects.all().delete()
        Gallery.objects.all().delete()
        News.objects.all().delete()
        FamilyMedia.objects.all().delete()
        DeceasedMember.objects.all().delete()
        FamilyMember.objects.all().delete()
        FamilyHead.objects.all().delete()
        Family.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()

        # Re-create Superuser
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin', member_id='ADMIN001')
            self.stdout.write('Created superuser: admin')

        # 2. Setup Base Family
        self.stdout.write('Creating Root Ancestors...')
        main_family = Family.objects.create(
            sl_no="1",
            branch="Main Branch",
            member_no="FAM001"
        )

        all_members = []
        created_users = []

        # Helper to create a member
        def create_member(generation, gender, parents=None, spouse=None, surname="Kollaparambil"):
            
            # 50% chance to have a user account (if alive-ish - we assume all created here are alive for simplicity)
            user_account = None
            if random.random() > 0.4:
                first_name = fake.first_name_male() if gender == 'M' else fake.first_name_female()
                username = f"{first_name.lower()}{random.randint(100,999)}"
                email = f"{username}@example.com"
                
                if not User.objects.filter(username=username).exists():
                    user_account = User.objects.create_user(
                        username=username,
                        email=email,
                        password='password123',
                        member_id=f"MEM{random.randint(10000, 99999)}",
                        first_name=first_name,
                        last_name=surname
                    )
                    # Avatar
                    if random.random() > 0.3:
                         user_account.avatar.save(f'avatar_{username}.jpg', generate_image(200, 200), save=True)
                    created_users.append(user_account)
            
            name = (user_account.first_name + " " + user_account.last_name) if user_account else fake.name_male() if gender == 'M' else fake.name_female()
            
            # Age based on generation (approx)
            base_age = 90 - (generation * 25) # Gen 0=90, Gen 1=65, Gen 2=40, Gen 3=15
            age = max(1, base_age + random.randint(-5, 5))
            dob = datetime.date.today() - datetime.timedelta(days=age*365)

            mem = FamilyMember.objects.create(
                family=main_family,
                user=user_account,
                temp_member_id=f"TEMP{random.randint(100000,999999)}",
                name=name,
                age=age,
                gender=gender,
                relation="Head" if generation == 0 else "Member", # Simplified, purely visual field often
                date_of_birth=dob,
                address_if_different=fake.address(),
                education=fake.job() if age > 20 else "Student",
                occupation=fake.job() if age > 20 else "Student",
                place_of_work=fake.city() if age > 20 else "School",
                blood_group=random.choice(['A+', 'B+', 'O+', 'AB+', 'A-', 'O-']),
                bio=fake.paragraph(nb_sentences=3)
            )
            
            if parents:
                mem.parents.set(parents)
            
            if spouse:
                mem.spouse = spouse
                mem.save()
                spouse.spouse = mem
                spouse.save()
            
            all_members.append(mem)
            return mem

        # --- Tree Generation ---
        
        # Gen 0: Roots
        grandfather = create_member(0, 'M')
        grandmother = create_member(0, 'F', spouse=grandfather)

        # Gen 1: 4 Children
        gen1_couples = []
        for i in range(4):
            child_gender = random.choice(['M', 'F'])
            child = create_member(1, child_gender, parents=[grandfather, grandmother])
            
            # 80% chance to marry
            if random.random() > 0.2:
                spouse_gender = 'F' if child_gender == 'M' else 'M'
                spouse = create_member(1, spouse_gender) # Spouse linked via marriage logic in helper
                
                # Link them
                child.spouse = spouse
                child.save()
                spouse.spouse = child
                spouse.save()
                
                gen1_couples.append((child, spouse))
            
        # Gen 2: Grandchildren
        gen2_couples = []
        for p1, p2 in gen1_couples:
            num_kids = random.randint(2, 4)
            for j in range(num_kids):
                bgender = random.choice(['M', 'F'])
                grandchild = create_member(2, bgender, parents=[p1, p2])
                
                # 60% chance to marry
                if random.random() > 0.4:
                     sp_gender = 'F' if bgender == 'M' else 'M'
                     sp = create_member(2, sp_gender)
                     grandchild.spouse = sp
                     grandchild.save()
                     sp.spouse = grandchild
                     sp.save()
                     gen2_couples.append((grandchild, sp))

        # Gen 3: Great-Grandchildren
        for p1, p2 in gen2_couples:
             num_kids = random.randint(1, 3)
             for k in range(num_kids):
                 create_member(3, random.choice(['M', 'F']), parents=[p1, p2])

        self.stdout.write(f'Generated {len(all_members)} connected family members.')

        # 7. Other Data (News, Gallery etc) using created users
        self.stdout.write('Creating News, Events, Gallery...')
        if not created_users: # fallback
             created_users = [User.objects.first()]

        for i in range(20):
            News.objects.create(
                title=f"News: {fake.sentence()}",
                description=fake.paragraph(),
                image=generate_image(800, 400),
                type='news',
                 created_at=fake.date_time_this_year(tzinfo=timezone.get_current_timezone()),
                author=random.choice(created_users)
            )
            News.objects.create(
                title=f"Event: {fake.bs()}",
                description=fake.paragraph(),
                image=generate_image(800, 400),
                type='event',
                event_date=fake.future_datetime(tzinfo=timezone.get_current_timezone()),
                location=fake.address(),
                 created_at=fake.date_time_this_year(tzinfo=timezone.get_current_timezone()),
                author=random.choice(created_users)
            )
            Gallery.objects.create(
                image=generate_image(1024, 768),
                date=fake.date_this_year(),
                description=fake.catch_phrase()
            )

        self.stdout.write(self.style.SUCCESS(f'Successfully re-seeded with SINGLE CONNECTED TREE! Total Members: {len(all_members)}'))
