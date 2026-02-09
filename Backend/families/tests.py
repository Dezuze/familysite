from django.test import TestCase
from families.models import Family, FamilyMember
import datetime

class FamiliesTests(TestCase):
    def setUp(self):
        self.family = Family.objects.create(sl_no="1", branch="North", member_no="F100-TEST")
        self.member1 = FamilyMember.objects.create(
            family=self.family,
            name="Alice",
            age=50,
            relation="Parent",
            date_of_birth=datetime.date(1974, 5, 5),
            blood_group="A+",
            education="Master's",
            occupation="Teacher"
        )
        self.member2 = FamilyMember.objects.create(
            family=self.family,
            name="Bob",
            age=25,
            relation="Son",
            date_of_birth=datetime.date(1999, 10, 10),
            blood_group="A+",
            education="Bachelor's",
            occupation="Student"
        )

    def test_family_relationship(self):
        self.member2.parents.add(self.member1)
        self.assertIn(self.member1, self.member2.parents.all())
        self.assertIn(self.member2, self.member1.children.all())

    def test_family_str(self):
        self.assertEqual(str(self.family), "F100")
