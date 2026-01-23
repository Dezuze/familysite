from django.db import models
from django.conf import settings


class Family(models.Model):
    sl_no = models.CharField(max_length=20)
    branch = models.CharField(max_length=100)

    member_no = models.CharField(max_length=50, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.member_no


class FamilyHead(models.Model):
    family = models.OneToOneField(Family, on_delete=models.CASCADE, related_name="head")

    # optional link to a registered user
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    name = models.CharField(max_length=100)
    nickname = models.CharField(max_length=50, blank=True, null=True)

    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=1, choices=[("M", "Male"), ("F", "Female"), ("O", "Other")])

    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()

    church = models.CharField(max_length=100)
    education = models.CharField(max_length=100)
    occupation = models.CharField(max_length=100)


class FamilyMember(models.Model):
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="members")

    # optional link to accounts.User if the person has an account
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    # temporary id for unregistered persons
    temp_member_id = models.CharField(max_length=50, blank=True, null=True)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    nickname = models.CharField(max_length=50, blank=True, null=True)
    
    gender = models.CharField(max_length=10, choices=[("M", "Male"), ("F", "Female"), ("O", "Other")], default='M')
    
    date_of_birth = models.DateField(null=True, blank=True)
    
    is_deceased = models.BooleanField(default=False)
    date_of_death = models.DateField(null=True, blank=True)
    crematory = models.CharField(max_length=255, blank=True, null=True)
    
    address = models.TextField(blank=True, null=True) # schema says address TEXT
    phone_no = models.CharField(max_length=20, blank=True, null=True)
    email_id = models.EmailField(max_length=100, blank=True, null=True)
    
    church_parish = models.CharField(max_length=255, blank=True, null=True)
    education = models.CharField(max_length=255, blank=True, null=True)
    occupation = models.CharField(max_length=255, blank=True, null=True)
    place_of_work = models.CharField(max_length=255, blank=True, null=True)
    blood_group = models.CharField(max_length=5, blank=True, null=True)
    
    # profile_pic_url in schema, mapped to ImageField here
    photo = models.ImageField(upload_to="members/photos/", blank=True, null=True)

    # SELF-REFERENCING RELATIONSHIP (The Tree)
    # Points to the parent member. Allows multiple children per parent.
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    
    # SPOUSAL RELATIONSHIP
    spouse = models.OneToOneField('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='spouse_ref')

    # Old bio field, keeping for backward compat or remove? Schema doesn't explicitly have bio but has address/education etc. 
    # Schema doesn't have 'bio'. I will remove 'bio' to strictly follow schema or keep as extra? 
    # User said "matching this structure". I'll keep bio if it's not conflicting, but I'll remove it if strictly matching.
    # I'll keep bio as extra field for now unless it causes issues.
    bio = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def age(self):
        from datetime import date
        today = date.today()
        if self.date_of_death:
            end_date = self.date_of_death
        else:
            end_date = today
        
        if not self.date_of_birth:
            return 0
            
        return end_date.year - self.date_of_birth.year - ((end_date.month, end_date.day) < (self.date_of_birth.month, self.date_of_birth.day))

    def __str__(self):
        return f"{self.first_name} {self.last_name or ''}".strip()


class FamilyMedia(models.Model):
    CATEGORY_CHOICES = [
        ("family", "Family"),
        ("wedding", "Wedding"),
        ("achievement", "Achievement"),
    ]

    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="media")

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to="family/gallery/")
