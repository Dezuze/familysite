import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker
from families.models import Family, FamilyHead, FamilyMember, DeceasedMember
from accounts.models import User
from news.models import Post

class Command(BaseCommand):
    help = 'Seeds the database with realistic Indian family data and complex relationships.'

    def handle(self, *args, **options):
        fake = Faker('en_IN')
        
        self.stdout.write("Purging existing data...")
        # Order of deletion to avoid FK issues
        User.objects.filter(is_superuser=False).exclude(username__in=['normal_user', 'admin_wesly']).delete()
        DeceasedMember.objects.all().delete()
        # Clear member links from preserved users first
        User.objects.filter(username__in=['normal_user', 'admin_wesly']).update(member=None)
        
        FamilyHead.objects.all().delete()
        FamilyMember.objects.all().delete()
        Family.objects.all().delete()
        Post.objects.all().delete()

        self.stdout.write("Generating realistic Indian family data...")
        
        # Get preserved users
        normal_user = User.objects.filter(username='normal_user').first()
        admin_wesly = User.objects.filter(username='admin_wesly').first()

        family_branches = ["Vadakara", "Thalassery", "Kottayam", "Pala", "Kakkanad", "Edappally"]
        occupations = ["Software Engineer", "Retired Teacher", "Nurse", "Farmer", "Business Owner", "Doctor", "Banker", "Student"]
        churches = ["St. Mary's Church", "St. George Cathedral", "Holy Family Parish", "Emmanuel Mar Thoma"]

        for i in range(1, 11):  # Create 10 realistic families
            branch = random.choice(family_branches)
            member_no = f"KFA-B{i}-{random.randint(1000, 9999)}"
            
            with transaction.atomic():
                fam = Family.objects.create(
                    sl_no=str(i),
                    branch=branch,
                    member_no=member_no
                )

                # 1. Set up the Head (Father or Widow)
                is_widow = random.random() < 0.2
                head_gender = 'M' if not is_widow else 'F'
                head_name = fake.name_male() if head_gender == 'M' else fake.name_female()
                head_age = random.randint(50, 85)
                
                head_member = FamilyMember.objects.create(
                    family=fam,
                    name=head_name,
                    age=head_age,
                    relation="Self (Head)" if not is_widow else "Widow (Head)",
                    date_of_birth=date.today() - timedelta(days=head_age * 365),
                    education="Post Graduate" if random.random() > 0.5 else "Graduate",
                    occupation=random.choice(occupations),
                    blood_group=random.choice(['A+', 'B+', 'O+', 'AB+']),
                )
                
                # Link admin_wesly to the first head
                if i == 1 and admin_wesly:
                    admin_wesly.member = head_member
                    admin_wesly.save()

                FamilyHead.objects.create(
                    family=fam,
                    name=head_name,
                    age=head_age,
                    gender=head_gender,
                    address=fake.address(),
                    phone=fake.phone_number()[:15],
                    email=fake.email(),
                    church=random.choice(churches),
                    education=head_member.education,
                    occupation=head_member.occupation
                )

                # 2. The Spouse (if not widow)
                spouse = None
                if not is_widow:
                    spouse_name = fake.name_female()
                    spouse_age = head_age - random.randint(-5, 5)
                    spouse = FamilyMember.objects.create(
                        family=fam,
                        name=spouse_name,
                        age=spouse_age,
                        relation="Wife",
                        date_of_birth=date.today() - timedelta(days=spouse_age * 365),
                        education="Graduate",
                        occupation="Homemaker" if random.random() > 0.4 else random.choice(occupations),
                        blood_group=random.choice(['A+', 'B+', 'O+', 'AB+']),
                    )
                    
                    # Link normal_user to the first spouse
                    if i == 1 and normal_user:
                        normal_user.member = spouse
                        normal_user.save()

                # 3. Children (Nuclear, Step-children, etc.)
                num_children = random.randint(1, 4)
                for c in range(num_children):
                    child_age = random.randint(5, 40)
                    
                    # Randomize relationship for complexity
                    rand = random.random()
                    if rand < 0.1:
                        rel = "Step-son" if random.random() > 0.5 else "Step-daughter"
                    elif rand < 0.2:
                        rel = "Divorced Son" if random.random() > 0.5 else "Divorced Daughter"
                    else:
                        rel = "Son" if random.random() > 0.5 else "Daughter"

                    child = FamilyMember.objects.create(
                        family=fam,
                        name=fake.name_male() if "Son" in rel else fake.name_female(),
                        age=child_age,
                        relation=rel,
                        date_of_birth=date.today() - timedelta(days=child_age * 365),
                        education="Schooling" if child_age < 18 else "Engineer/Arts",
                        occupation="Student" if child_age < 23 else random.choice(occupations),
                        blood_group=random.choice(['A+', 'B+', 'O+', 'AB+']),
                    )
                    
                    # Link parents
                    parent_list = [head_member]
                    if spouse: parent_list.append(spouse)
                    child.parents.set(parent_list)

                # 4. Deceased Records for this family
                if random.random() < 0.5:
                    d_age = random.randint(70, 95)
                    d_death_year = random.randint(1990, 2024)
                    DeceasedMember.objects.create(
                        family=fam,
                        name=fake.name_male(),
                        age_at_death=d_age,
                        relation="Grandfather",
                        date_of_birth=date(d_death_year - d_age, 1, 1),
                        date_of_death=date(d_death_year, 1, 1),
                        crematory=f"{branch} Parish Cemetery"
                    )

        # 5. Seed some News
        for j in range(5):
            Post.objects.create(
                creator=FamilyMember.objects.order_by('?').first(),
                post_type='news',
                title=f"Annual {random.choice(family_branches)} Branch Meetup {2026}",
                description=fake.paragraph(),
                location=random.choice(family_branches)
            )

        self.stdout.write(self.style.SUCCESS("Successfully seeded 10 realistic Indian families with complex relations and linked users!"))
