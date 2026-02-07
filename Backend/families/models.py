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

    name = models.CharField(max_length=100)
    nickname = models.CharField(max_length=50, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[("M", "Male"), ("F", "Female"), ("O", "Other")], default="M")
    
    age = models.PositiveIntegerField()
    relation = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    
    is_deceased = models.BooleanField(default=False)
    date_of_death = models.DateField(blank=True, null=True)

    address = models.TextField(blank=True, null=True)
    phone_no = models.CharField(max_length=20, blank=True, null=True)
    email_id = models.CharField(max_length=100, blank=True, null=True)
    church_parish = models.CharField(max_length=255, blank=True, null=True)

    education = models.CharField(max_length=100)
    occupation = models.CharField(max_length=100)
    place_of_work = models.CharField(max_length=100, blank=True, null=True)
    blood_group = models.CharField(max_length=5)
    
    bio = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to="members/photos/", blank=True, null=True)

    # Tree relationships
    spouse = models.OneToOneField(
        'self',
        on_delete=models.SET_NULL,
        related_name='husband_or_wife',
        null=True,
        blank=True
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        related_name='children_node',
        null=True,
        blank=True
    )

    # Legacy/Group relationships
    parents = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='children',
        blank=True,
    )


class DeceasedMember(models.Model):
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="deceased")

    name = models.CharField(max_length=100)
    age_at_death = models.PositiveIntegerField()

    relation = models.CharField(max_length=50)

    date_of_birth = models.DateField()
    date_of_death = models.DateField()

    crematory = models.CharField(max_length=100)

    photo = models.ImageField(upload_to="deceased/photos/", blank=True, null=True)


class FamilyMedia(models.Model):
    CATEGORY_CHOICES = [
        ("family", "Family"),
        ("wedding", "Wedding"),
        ("achievement", "Achievement"),
    ]

    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="media")

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to="family/gallery/")
