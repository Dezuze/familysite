import random
import os
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from django.core.files import File
from faker import Faker
from families.models import Family, FamilyHead, FamilyMember, DeceasedMember
from accounts.models import User
from news.models import Post

from profiles.models import Committee

class Command(BaseCommand):
    help = 'Purges and re-populates the database with realistic family data, photos, and committee roles.'

    def handle(self, *args, **options):
        fake = Faker('en_IN')
        test_dir = r'c:\Users\wesly\OneDrive\Documents\Coding\Project\test'
        
        # Get all test images
        if not os.path.exists(test_dir):
            self.stdout.write(self.style.ERROR(f"Test directory not found: {test_dir}"))
            return

        test_images = [f for f in os.listdir(test_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
        if not test_images:
            self.stdout.write(self.style.ERROR(f"No images found in {test_dir}"))
            return

        self.stdout.write("Purging existing data...")
        # Preserve specific users
        User.objects.filter(is_superuser=False).exclude(username__in=['normal_user', 'admin_wesly']).delete()
        DeceasedMember.objects.all().delete()
        Committee.objects.all().delete()
        
        # Disconnect members from preserved users
        User.objects.filter(username__in=['normal_user', 'admin_wesly']).update(member=None)
        
        FamilyHead.objects.all().delete()
        FamilyMember.objects.all().delete()
        Family.objects.all().delete()
        Post.objects.all().delete()

        self.stdout.write("Generating fresh family data and assigning photos...")
        
        normal_user = User.objects.filter(username='normal_user').first()
        admin_wesly = User.objects.filter(username='admin_wesly').first()

        family_branches = ["Vadakara", "Thalassery", "Kottayam", "Pala", "Kakkanad", "Edappally"]
        occupations = ["Software Engineer", "Retired Teacher", "Nurse", "Farmer", "Business Owner", "Doctor", "Banker", "Student"]
        churches = ["St. Mary's Church", "St. George Cathedral", "Holy Family Parish", "Emmanuel Mar Thoma"]

        all_created_members = []

        for i in range(1, 11): 
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
                    gender=head_gender,
                    relation="Self (Head)" if not is_widow else "Widow (Head)",
                    date_of_birth=date.today() - timedelta(days=head_age * 365),
                    education="Post Graduate" if random.random() > 0.5 else "Graduate",
                    occupation=random.choice(occupations),
                    blood_group=random.choice(['A+', 'B+', 'O+', 'AB+']),
                )
                self.assign_photo(head_member, test_dir, test_images)
                all_created_members.append(head_member)

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
                        gender='F',
                        relation="Wife",
                        date_of_birth=date.today() - timedelta(days=spouse_age * 365),
                        education="Graduate",
                        occupation="Homemaker" if random.random() > 0.4 else random.choice(occupations),
                        blood_group=random.choice(['A+', 'B+', 'O+', 'AB+']),
                    )
                    self.assign_photo(spouse, test_dir, test_images)
                    all_created_members.append(spouse)
                    
                    # Link normal_user to the first spouse
                    if i == 1 and normal_user:
                        normal_user.member = spouse
                        normal_user.save()

                # 3. Children
                num_children = random.randint(1, 4)
                for c in range(num_children):
                    child_age = random.randint(5, 40)
                    rel = "Son" if random.random() > 0.5 else "Daughter"
                    child = FamilyMember.objects.create(
                        family=fam,
                        name=fake.name_male() if rel == "Son" else fake.name_female(),
                        age=child_age,
                        gender='M' if rel == "Son" else 'F',
                        relation=rel,
                        date_of_birth=date.today() - timedelta(days=child_age * 365),
                        education="Schooling" if child_age < 18 else "Engineer/Arts",
                        occupation="Student" if child_age < 23 else random.choice(occupations),
                        blood_group=random.choice(['A+', 'B+', 'O+', 'AB+']),
                    )
                    self.assign_photo(child, test_dir, test_images)
                    all_created_members.append(child)
                    
                    # Link parents
                    parent_list = [head_member]
                    if spouse: parent_list.append(spouse)
                    child.parents.set(parent_list)

        # 4. Create Committee Roles for 5 random members
        self.stdout.write("Assigning Committee Roles...")
        roles = ["President", "Secretary", "Treasurer", "Coordinator", "Executive Member"]
        random.shuffle(all_created_members)
        
        for idx, role in enumerate(roles):
            if idx < len(all_created_members):
                member = all_created_members[idx]
                # Check if member already has user account, otherwise create one
                user_account = getattr(member, 'user_account', None)
                if not user_account:
                    username = f"{member.name.split()[0].lower()}_{random.randint(100, 999)}"
                    user_account = User.objects.create_user(
                        username=username,
                        email=f"{username}@kollamparambil.com",
                        password="password123",
                        member=member
                    )
                
                # Create Committee Entry
                Committee.objects.create(
                    user=user_account,
                    role=role,
                    pic=member.photo if member.photo else None
                )

        self.stdout.write(self.style.SUCCESS("Successfully re-populated database with committee roles and photos!"))

    def assign_photo(self, member, test_dir, images):
        img_name = random.choice(images)
        img_path = os.path.join(test_dir, img_name)
        with open(img_path, 'rb') as f:
            member.photo.save(img_name, File(f), save=True)
