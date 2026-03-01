"""
Families App Models
===================
Core data models for the Kollamparambil Family application.

Models:
    - Family: Root unit grouping members by branch/household.
    - FamilyHead: Designated leader of a Family branch.
    - FamilyMember: Individual member with profile, demographics, and relationships.
    - DeceasedMember: Archived record of deceased family members.
    - FamilyMedia: Gallery images categorised by event type.
    - Relationship: Directed edge between two FamilyMembers encoding a named
      relation (Father, Spouse, Uncle, etc.) used by the tree-builder.
"""
from django.db import models
from django.conf import settings


class Family(models.Model):
    """Root family unit identified by a unique member number."""
    sl_no = models.CharField(max_length=20)
    branch = models.CharField(max_length=100)

    member_no = models.CharField(max_length=50, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.member_no


class FamilyHead(models.Model):
    """Designated head (eldest/primary contact) of a Family branch."""
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
    """
    Individual family member with full profile data.

    Key fields:
        - relation: Default relation label (Father, Brother, etc.).
        - parents: M2M self-referential field for hierarchical tree rendering.
        - created_by: The User who added this member (guardian pattern).
        - is_independent: When True, the member controls their own profile.

    Properties:
        - role: Returns committee role if available, else falls back to `relation`.
        - is_committee: True if the linked user sits on a committee.
    """
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="members")

    # link to accounts.User handled by User.member (OneToOneField)
    # temporary id for unregistered persons
    temp_member_id = models.CharField(max_length=50, blank=True, null=True)

    name = models.CharField(max_length=100)
    nickname = models.CharField(max_length=50, blank=True, null=True)
    age = models.PositiveIntegerField(null=True, blank=True)

    RELATION_CHOICES = [
        ('Head', 'Head'),
        ('Spouse', 'Spouse'),
        ('Father', 'Father'),
        ('Mother', 'Mother'),
        ('Son', 'Son'),
        ('Daughter', 'Daughter'),
        ('Brother', 'Brother'),
        ('Sister', 'Sister'),
        ('Grandfather', 'Grandfather'),
        ('Grandmother', 'Grandmother'),
        ('Grandson', 'Grandson'),
        ('Granddaughter', 'Granddaughter'),
        ('Uncle', 'Uncle'),
        ('Aunt', 'Aunt'),
        ('Nephew', 'Nephew'),
        ('Niece', 'Niece'),
        ('Cousin', 'Cousin'),
        ('Father-in-law', 'Father-in-law'),
        ('Mother-in-law', 'Mother-in-law'),
        ('Son-in-law', 'Son-in-law'),
        ('Daughter-in-law', 'Daughter-in-law'),
        ('Brother-in-law', 'Brother-in-law'),
        ('Sister-in-law', 'Sister-in-law'),
        ('Other', 'Other'),
    ]

    relation = models.CharField(max_length=50, choices=RELATION_CHOICES, default='Other')
    date_of_birth = models.DateField(null=True, blank=True)

    address_if_different = models.TextField(blank=True, null=True)

    education = models.CharField(max_length=100, blank=True, null=True)
    occupation = models.CharField(max_length=100, blank=True, null=True)
    place_of_work = models.CharField(max_length=100, blank=True, null=True)

    blood_group = models.CharField(max_length=10, blank=True, null=True)
    is_deceased = models.BooleanField(default=False)
    is_independent = models.BooleanField(default=False, help_text="When True, the creator/guardian loses write access and the profile owner has full control.")
    date_of_death = models.DateField(null=True, blank=True)

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
        """Return committee role title if member is on a committee, else relation label."""
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
        """True if this member's linked user account has any committee entries."""
        try:
            if hasattr(self, 'user_account') and self.user_account:
                return self.user_account.committee_entries.exists()
        except Exception:
            pass
        return False

    def __str__(self):
        return f"{self.name} ({self.role})"


class DeceasedMember(models.Model):
    """Archived record for a deceased family member (separate from FamilyMember.is_deceased)."""
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="deceased")

    name = models.CharField(max_length=100)
    age_at_death = models.PositiveIntegerField()

    relation = models.CharField(max_length=50)

    date_of_birth = models.DateField()
    date_of_death = models.DateField()

    crematory = models.CharField(max_length=100)

    photo = models.ImageField(upload_to="deceased/photos/", blank=True, null=True)


class FamilyMedia(models.Model):
    """Gallery image uploaded under a specific category (family, wedding, achievement)."""
    CATEGORY_CHOICES = [
        ("family", "Family"),
        ("wedding", "Wedding"),
        ("achievement", "Achievement"),
    ]

    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="media")

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to="family/gallery/")


class Relationship(models.Model):
    """
    Directed relationship edge: from_member --[relation_type]--> to_member.

    Interpretation: "from_member says to_member is their <relation_type>."
    Example: Relationship(from=Alex, to=John, type='Father') means
             "Alex says John is his Father".

    The GENDER_MAP class attribute auto-assigns gender when new members are
    created through the onboarding flow.
    """
    RELATION_CHOICES = [
        ("Father", "Father"),
        ("Mother", "Mother"),
        ("Son", "Son"),
        ("Daughter", "Daughter"),
        ("Spouse", "Spouse"),
        ("Brother", "Brother"),
        ("Sister", "Sister"),
        ("Grandfather", "Grandfather"),
        ("Grandmother", "Grandmother"),
        ("Paternal Grandfather", "Paternal Grandfather"),
        ("Paternal Grandmother", "Paternal Grandmother"),
        ("Maternal Grandfather", "Maternal Grandfather"),
        ("Maternal Grandmother", "Maternal Grandmother"),
        ("Grandson", "Grandson"),
        ("Granddaughter", "Granddaughter"),
        ("Uncle", "Uncle"),
        ("Aunt", "Aunt"),
        ("Nephew", "Nephew"),
        ("Niece", "Niece"),
        ("Cousin", "Cousin"),
        ("Father-in-law", "Father-in-law"),
        ("Mother-in-law", "Mother-in-law"),
        ("Son-in-law", "Son-in-law"),
        ("Daughter-in-law", "Daughter-in-law"),
        ("Brother-in-law", "Brother-in-law"),
        ("Sister-in-law", "Sister-in-law"),
        ("Other", "Other"),
    ]

    # Gender auto-assignment map
    GENDER_MAP = {
        'Father': 'M', 'Mother': 'F',
        'Son': 'M', 'Daughter': 'F',
        'Brother': 'M', 'Sister': 'F',
        'Grandfather': 'M', 'Grandmother': 'F',
        'Paternal Grandfather': 'M', 'Paternal Grandmother': 'F',
        'Maternal Grandfather': 'M', 'Maternal Grandmother': 'F',
        'Grandson': 'M', 'Granddaughter': 'F',
        'Uncle': 'M', 'Aunt': 'F',
        'Nephew': 'M', 'Niece': 'F',
        'Father-in-law': 'M', 'Mother-in-law': 'F',
        'Son-in-law': 'M', 'Daughter-in-law': 'F',
        'Brother-in-law': 'M', 'Sister-in-law': 'F',
    }

    from_member = models.ForeignKey(FamilyMember, on_delete=models.CASCADE, related_name="relationships_from")
    to_member = models.ForeignKey(FamilyMember, on_delete=models.CASCADE, related_name="relationships_to")
    relation_type = models.CharField(max_length=50, choices=RELATION_CHOICES)

    class Meta:
        unique_together = ('from_member', 'to_member', 'relation_type')

    def __str__(self):
        return f"{self.from_member.name} -> {self.relation_type} -> {self.to_member.name}"
