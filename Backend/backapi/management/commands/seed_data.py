from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from families.models import Family, FamilyMember
from news.models import News, Event
from profiles.models import Gallery, Committee
from faker import Faker
import random
from django.utils import timezone
from datetime import timedelta
from django.core.files.base import ContentFile
import io
from PIL import Image

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with initial data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')
        fake = Faker()
        
        # Cleanup
        self.stdout.write('Cleaning up old data...')
        User.objects.all().delete()
        Family.objects.all().delete()
        News.objects.all().delete()
        Gallery.objects.all().delete()
        Committee.objects.all().delete()

        # Create Superuser
        superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin',
            member_id='ADMIN001'
        )
        self.stdout.write(f'Created superuser: admin (pass: admin)')

        # Generate Fake Image
        def generate_image(width=400, height=400, color=None):
            if color is None:
                color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
            image = Image.new('RGB', (width, height), color)
            img_io = io.BytesIO()
            image.save(img_io, format='JPEG')
            return ContentFile(img_io.getvalue(), name=f'seed_{random.randint(0,1000)}.jpg')

        # Create Families (Branches)
        families = []
        for i in range(5):
            f = Family.objects.create(
                name=f"{fake.last_name()} Branch",
                description=fake.text()
            )
            families.append(f)

        # Create Users & Members
        self.stdout.write('Creating 30+ users...')
        users = []
        for i in range(35):
            profile = fake.profile()
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = f"{first_name.lower()}.{last_name.lower()}{i}"
            
            user = User.objects.create_user(
                username=username,
                email=profile['mail'],
                password='password123',
                member_id=f"MEM{1000+i}",
                first_name=first_name,
                last_name=last_name
            )
            
            # Avatar (50% chance)
            if random.choice([True, False]):
                user.avatar.save(f'avatar_{i}.jpg', generate_image(200, 200), save=True)
            
            users.append(user)

            # Family Member Profile
            family = random.choice(families)
            member = FamilyMember.objects.create(
                user=user,
                family=family,
                first_name=first_name,
                last_name=last_name,
                birth_date=fake.date_of_birth(),
                phone=fake.phone_number(),
                address=fake.address(),
                bio=fake.text(max_nb_chars=100)
            )

        # Create News & Events
        self.stdout.write('Creating News & Events...')
        for _ in range(30):
            author = random.choice(users)
            # News
            News.objects.create(
                title=fake.sentence(),
                content=fake.paragraph(),
                author=author,
                created_at=fake.date_time_this_year(tzinfo=timezone.get_current_timezone()),
                image=generate_image(800, 400) if random.choice([True, False]) else None
            )
            # Event
            Event.objects.create(
                title=f"Event: {fake.bs()}",
                description=fake.paragraph(),
                date=fake.future_date_time(tzinfo=timezone.get_current_timezone()),
                location=fake.city(),
                author=author
            )

        # Create Gallery
        self.stdout.write('Creating Gallery...')
        for _ in range(30):
             Gallery.objects.create(
                 image=generate_image(random.randint(600, 1000), random.randint(400, 800)),
                 date=fake.date_this_year(),
                 description=fake.sentence()
             )
        
        # Committee
        self.stdout.write('Creating Committee...')
        for _ in range(5):
             u = random.choice(users)
             Committee.objects.create(
                 user=u,
                 role=fake.job(),
                 pic=generate_image(300, 300)
             )

        self.stdout.write(self.style.SUCCESS('Successfully seeded database!'))
