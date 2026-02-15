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

    # link to accounts.User handled by User.member (OneToOneField)
    # temporary id for unregistered persons
    temp_member_id = models.CharField(max_length=50, blank=True, null=True)

    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()

    relation = models.CharField(max_length=50)
    date_of_birth = models.DateField()

    address_if_different = models.TextField(blank=True, null=True)

    education = models.CharField(max_length=100)
    occupation = models.CharField(max_length=100)
    place_of_work = models.CharField(max_length=100, blank=True, null=True)

    blood_group = models.CharField(max_length=5)

    gender = models.CharField(max_length=1, choices=[("M", "Male"), ("F", "Female"), ("O", "Other")], default="M")
    bio = models.TextField(blank=True, null=True)
    phone_no = models.CharField(max_length=20, blank=True, null=True)
    email_id = models.EmailField(blank=True, null=True)
    church_parish = models.CharField(max_length=100, blank=True, null=True)

    photo = models.ImageField(upload_to="members/photos/", blank=True, null=True)

    # Link to other FamilyMember instances to represent parent/child relationships.
    # Use `symmetrical=False` so `parents` and `children` are distinct.
    # Track who created this member (especially for children/members without accounts)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="managed_members",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    parents = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='children',
        blank=True,
    )

    @property
    def role(self):
        # Check if linked user is in committee
        try:
            if hasattr(self, 'user_account') and self.user_account:
                committee_entry = self.user_account.committee_entries.first()
                if committee_entry and committee_entry.role:
                    return committee_entry.role
        except Exception:
            pass
        return self.relation

    @property
    def is_committee(self):
        try:
            if hasattr(self, 'user_account') and self.user_account:
                return self.user_account.committee_entries.exists()
        except Exception:
            pass
        return False

    def __str__(self):
        return f"{self.name} ({self.role})"


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
