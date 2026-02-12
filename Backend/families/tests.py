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
        self.assertEqual(str(self.family), "F100-TEST")

    def test_update_parents_via_api(self):
        from rest_framework.test import APIClient
        client = APIClient()
        # Note: In a real scenario we'd need to mock authentication or use a logged in user
        # For this test, we verify the view logic if it were called
        url = '/api/families/profile/'
        data = {
            'parents': [self.member1.id]
        }
        # Since we use credentials='include' and session auth, we'll manually set the user
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(username="testuser", email="test@ex.com", member=self.member2)
        client.force_authenticate(user=user)
        
        response = client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        
        self.member2.refresh_from_db()
        self.assertIn(self.member1, self.member2.parents.all())
